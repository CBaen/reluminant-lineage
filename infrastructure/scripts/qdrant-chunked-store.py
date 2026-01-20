#!/usr/bin/env python3
"""
qdrant-chunked-store.py - Store research with proper chunking and parent-child linking

Takes text input, chunks it (400-800 words with overlap), stores each chunk as a
linked Qdrant point. Creates/updates parent summary point.

Usage:
  echo "LONG_TEXT" | python qdrant-chunked-store.py \
    --topic "topic-name" \
    --perspective "perspective-name" \
    --session "SessionName" \
    --collection "lineage_research"

Output: JSON with parent_id, source_id, chunks_stored, total_words, chunk_ids
"""

import argparse
import json
import sys
import uuid
import hashlib
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_DIM = 768

# Chunking parameters
MIN_CHUNK_WORDS = 400
MAX_CHUNK_WORDS = 800
OVERLAP_RATIO = 0.15  # 15% overlap


def get_ollama_embedding(text, model="nomic-embed-text"):
    """Get embedding from local Ollama instance."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": model, "prompt": text[:8000]},
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            embedding = data.get("embedding", [])
            if embedding and len(embedding) == EMBEDDING_DIM:
                return embedding
    except Exception as e:
        print(f"Ollama error: {e}", file=sys.stderr)
    return None


def get_hash_embedding(text):
    """Fallback: deterministic pseudo-embedding from hash."""
    text_hash = hashlib.sha256(text.encode('utf-8', errors='replace')).hexdigest()
    embedding = []
    for i in range(EMBEDDING_DIM):
        hash_segment = int(text_hash[(i * 2) % 64:(i * 2) % 64 + 2], 16)
        embedding.append((hash_segment / 255.0) * 2 - 1)
    return embedding


def chunk_text(text, min_words=MIN_CHUNK_WORDS, max_words=MAX_CHUNK_WORDS, overlap_ratio=OVERLAP_RATIO):
    """
    Split text into overlapping chunks of 400-800 words.
    Tries to break at sentence boundaries.
    """
    # Split into words while preserving structure
    words = text.split()
    total_words = len(words)

    if total_words <= max_words:
        # Text is small enough for one chunk
        return [text]

    chunks = []
    overlap_words = int(max_words * overlap_ratio)
    target_chunk_size = (min_words + max_words) // 2  # ~600 words

    start = 0
    while start < total_words:
        # Calculate end position
        end = min(start + target_chunk_size, total_words)

        # If not at the end, try to extend to sentence boundary
        if end < total_words:
            # Look forward up to max_words for a sentence end
            search_end = min(start + max_words, total_words)
            chunk_text_temp = ' '.join(words[start:search_end])

            # Find last sentence boundary
            sentence_ends = list(re.finditer(r'[.!?]\s+', chunk_text_temp))
            if sentence_ends:
                # Use the last sentence boundary that keeps us in range
                for match in reversed(sentence_ends):
                    boundary_pos = len(chunk_text_temp[:match.end()].split())
                    if min_words <= boundary_pos <= max_words:
                        end = start + boundary_pos
                        break

        # Extract chunk
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)

        # Move start position with overlap
        start = end - overlap_words if end < total_words else total_words

    return chunks


def generate_source_id(topic, perspective):
    """Generate unique source_id for this research."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    hash_suffix = hashlib.md5(f"{topic}{perspective}{timestamp}".encode()).hexdigest()[:8]
    return f"{topic}-{perspective}-{hash_suffix}"


def sanitize_payload(obj):
    """Recursively sanitize strings in payload for UTF-8 safety."""
    if isinstance(obj, str):
        return obj.encode('utf-8', errors='replace').decode('utf-8')
    if isinstance(obj, dict):
        return {k: sanitize_payload(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_payload(item) for item in obj]
    return obj


def store_point(collection, point_id, vector, payload):
    """Store a single point in Qdrant."""
    url = f"{QDRANT_URL}/collections/{collection}/points"

    data = {
        "points": [{
            "id": point_id,
            "vector": vector,
            "payload": sanitize_payload(payload)
        }]
    }

    response = requests.put(url, json=data, headers={"Content-Type": "application/json"})
    return response.json()


def store_points_batch(collection, points):
    """
    Store multiple points in a single Qdrant API call.

    Args:
        collection: Qdrant collection name
        points: List of dicts with 'id', 'vector', 'payload' keys

    Returns:
        API response dict
    """
    url = f"{QDRANT_URL}/collections/{collection}/points"

    data = {
        "points": [
            {
                "id": p["id"],
                "vector": p["vector"],
                "payload": sanitize_payload(p["payload"])
            }
            for p in points
        ]
    }

    response = requests.put(url, json=data, headers={"Content-Type": "application/json"})
    return response.json()


def ensure_collection_exists(collection):
    """Create collection if it doesn't exist."""
    response = requests.get(f"{QDRANT_URL}/collections/{collection}")
    if response.status_code == 200:
        return True

    create_response = requests.put(
        f"{QDRANT_URL}/collections/{collection}",
        json={
            "vectors": {
                "size": EMBEDDING_DIM,
                "distance": "Cosine"
            }
        }
    )
    return create_response.status_code == 200


def find_or_create_summary(collection, topic):
    """Find existing summary point for topic, or return None."""
    # Search for existing summary
    response = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/scroll",
        json={
            "filter": {
                "must": [
                    {"key": "type", "match": {"value": "summary"}},
                    {"key": "topic", "match": {"value": topic}}
                ]
            },
            "limit": 1,
            "with_payload": True
        }
    )

    if response.status_code == 200:
        result = response.json().get("result", {})
        points = result.get("points", [])
        if points:
            return points[0]["id"], points[0]["payload"]

    return None, None


def main():
    parser = argparse.ArgumentParser(description="Store research with chunking and parent-child linking")
    parser.add_argument("--topic", required=True, help="Research topic")
    parser.add_argument("--perspective", required=True, help="Perspective/angle of this research")
    parser.add_argument("--session", default="Unknown", help="Session name for attribution")
    parser.add_argument("--collection", default="lineage_research", help="Qdrant collection")
    parser.add_argument("--categories", default="", help="Comma-separated categories")

    args = parser.parse_args()

    # Read input
    input_text = sys.stdin.read().strip()
    if not input_text:
        print(json.dumps({"error": "No input received"}))
        sys.exit(1)

    # Ensure collection exists
    ensure_collection_exists(args.collection)

    # Generate source_id
    source_id = generate_source_id(args.topic, args.perspective)

    # Chunk the text
    chunks = chunk_text(input_text)
    total_chunks = len(chunks)
    total_words = len(input_text.split())

    # Parse categories
    categories = [c.strip() for c in args.categories.split(",") if c.strip()]

    # Store each chunk
    chunk_ids = []
    timestamp = int(datetime.now().timestamp())

    # Generate embeddings in parallel for better throughput
    def embed_chunk(chunk_data):
        """Generate embedding for a single chunk."""
        idx, chunk_text = chunk_data
        embedding = get_ollama_embedding(chunk_text)
        if not embedding:
            embedding = get_hash_embedding(chunk_text)
            return idx, embedding, "hash"
        return idx, embedding, "ollama"

    # Parallel embedding with ThreadPoolExecutor
    # Testing showed: 32 workers can process 32 embeddings in ~2.4s (GPU batching)
    # Use min(chunk_count, 32) workers for optimal throughput
    embeddings = [None] * total_chunks
    embedding_sources = ["hash"] * total_chunks
    optimal_workers = min(total_chunks, 32)

    with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
        futures = {executor.submit(embed_chunk, (i, chunk)): i for i, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            idx, embedding, source = future.result()
            embeddings[idx] = embedding
            embedding_sources[idx] = source
            if source == "hash":
                print(f"Warning: Using hash fallback for chunk {idx}", file=sys.stderr)

    # Build all points for batch storage
    points_to_store = []
    for i, chunk in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        word_count = len(chunk.split())

        payload = {
            "type": "chunk",
            "text": chunk,
            "source_id": source_id,
            "chunk_index": i,
            "total_chunks": total_chunks,
            "topic": args.topic,
            "perspective": args.perspective,
            "category": categories,
            "timestamp": timestamp,
            "word_count": word_count,
            "session": args.session,
            "embedding_source": embedding_sources[i]
        }

        points_to_store.append({
            "id": chunk_id,
            "vector": embeddings[i],
            "payload": payload
        })
        chunk_ids.append(chunk_id)

    # Batch store all chunks in single API call
    if points_to_store:
        result = store_points_batch(args.collection, points_to_store)
        if result.get("status") != "ok":
            print(f"Warning: Batch store issue: {result}", file=sys.stderr)
            # Clear chunk_ids if batch failed
            chunk_ids.clear()

    # Find or create summary point
    summary_id, existing_summary = find_or_create_summary(args.collection, args.topic)

    if summary_id:
        # Update existing summary
        existing_children = existing_summary.get("child_ids", [])
        existing_perspectives = existing_summary.get("perspectives", [])

        new_children = existing_children + chunk_ids
        new_perspectives = existing_perspectives + [{
            "name": args.perspective,
            "source_id": source_id,
            "word_count": total_words,
            "chunks": total_chunks
        }]

        # Update summary text
        summary_text = f"Topic: {args.topic}\n\nPerspectives researched:\n"
        for p in new_perspectives:
            summary_text += f"- {p['name']}: {p['word_count']} words, {p['chunks']} chunks\n"

        # Get embedding for summary
        summary_embedding = get_ollama_embedding(summary_text) or get_hash_embedding(summary_text)

        summary_payload = {
            "type": "summary",
            "text": summary_text,
            "topic": args.topic,
            "child_ids": new_children,
            "perspectives": new_perspectives,
            "timestamp": timestamp,
            "session": args.session
        }

        store_point(args.collection, summary_id, summary_embedding, summary_payload)
    else:
        # Create new summary
        summary_id = str(uuid.uuid4())
        summary_text = f"Topic: {args.topic}\n\nPerspectives researched:\n- {args.perspective}: {total_words} words, {total_chunks} chunks\n"

        summary_embedding = get_ollama_embedding(summary_text) or get_hash_embedding(summary_text)

        summary_payload = {
            "type": "summary",
            "text": summary_text,
            "topic": args.topic,
            "child_ids": chunk_ids,
            "perspectives": [{
                "name": args.perspective,
                "source_id": source_id,
                "word_count": total_words,
                "chunks": total_chunks
            }],
            "timestamp": timestamp,
            "session": args.session
        }

        store_point(args.collection, summary_id, summary_embedding, summary_payload)

    # Update chunks with parent_id
    for chunk_id in chunk_ids:
        requests.post(
            f"{QDRANT_URL}/collections/{args.collection}/points/payload",
            json={
                "payload": {"parent_id": summary_id},
                "points": [chunk_id]
            }
        )

    # Output result
    result = {
        "parent_id": summary_id,
        "source_id": source_id,
        "topic": args.topic,
        "perspective": args.perspective,
        "chunks_stored": len(chunk_ids),
        "total_words": total_words,
        "chunk_ids": chunk_ids
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
