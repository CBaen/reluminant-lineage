#!/usr/bin/env python3
"""
qdrant-store-gemini.py - Store Gemini's self-chunked research output

Takes Gemini's JSON output (already semantically chunked) and stores directly to Qdrant.
No dumb word-count chunking - Gemini did the semantic work.

SCHEMA VERSION: Supports both V1 (legacy) and V2 (2026 hybrid) schemas.
- V1: Single dense vector, legacy collection names
- V2: Named vectors (dense + sparse), universal_vault collection

Usage:
  # Hybrid storage to universal_vault (recommended)
  echo '{"meta": {...}, "chunks": [...]}' | python qdrant-store-gemini.py \
    --hybrid \
    --session "my-session"

  # Default collection is now universal_vault
  echo '{"meta": {...}, "chunks": [...]}' | python qdrant-store-gemini.py \
    --session "my-session"

Input: Gemini's JSON with meta, summary, and chunks array
Output: JSON with storage results
"""

import argparse
import json
import sys
import os
import uuid
import hashlib
from datetime import datetime
import requests

# Add scripts directory to path for local imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_DIM = 768
V2_COLLECTION = "universal_vault"  # 2026 migration target


def clean_gemini_output(text):
    """Strip markdown wrappers and noise from Gemini output."""
    import re

    # First, strip known prefixes that might appear on same line as JSON
    text = re.sub(r'^Loaded cached credentials\.?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'Loaded cached credentials\.?\s*', '', text)  # Also handle mid-text

    lines = text.strip().split('\n')
    cleaned = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Skip known noise lines
        if stripped.startswith('Error executing tool'):
            continue
        if not stripped:  # Skip empty lines at start
            if not cleaned:
                continue

        # Handle markdown code blocks
        if re.match(r'^```\s*(json)?\s*$', stripped, re.IGNORECASE):
            in_code_block = not in_code_block
            continue

        cleaned.append(line)

    result = '\n'.join(cleaned).strip()

    # Find JSON object by brace/bracket matching
    # We want to match the outermost {...} object, tracking all nested structures
    depth = 0
    start_idx = None
    start_char = None

    for i, char in enumerate(result):
        if char in '{[':
            if depth == 0 and char == '{':
                start_idx = i
                start_char = char
            depth += 1
        elif char in '}]':
            depth -= 1
            # Only return when we find the matching closing character for our start
            if depth == 0 and start_idx is not None:
                if (start_char == '{' and char == '}') or (start_char == '[' and char == ']'):
                    return result[start_idx:i+1]

    return result


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


def get_ollama_embeddings_batch(texts, model="nomic-embed-text"):
    """
    Get embeddings for multiple texts in parallel.

    Uses ThreadPoolExecutor for 32x throughput improvement.
    Research (2026-01-16) showed: T600 GPU can batch ~32 embeddings in parallel,
    completing all 32 in ~2.4s (vs ~69s sequential).

    Args:
        texts: List of text strings to embed
        model: Ollama model name

    Returns:
        List of embeddings (None for failed embeddings)
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if not texts:
        return []

    # For small batches, parallel overhead isn't worth it
    if len(texts) <= 2:
        return [get_ollama_embedding(t, model) for t in texts]

    results = [None] * len(texts)

    def embed_single(idx_text):
        idx, text = idx_text
        return idx, get_ollama_embedding(text, model)

    # Use min(chunk_count, 32) workers for optimal GPU batching
    # Testing showed 32 workers is the hardware ceiling for T600
    optimal_workers = min(len(texts), 32)

    with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
        futures = {executor.submit(embed_single, (i, t)): i for i, t in enumerate(texts)}
        for future in as_completed(futures):
            try:
                idx, embedding = future.result()
                results[idx] = embedding
            except Exception as e:
                print(f"Batch embedding error: {e}", file=sys.stderr)

    return results


def get_hash_embedding(text):
    """Fallback: deterministic pseudo-embedding from hash."""
    text_hash = hashlib.sha256(text.encode('utf-8', errors='replace')).hexdigest()
    embedding = []
    for i in range(EMBEDDING_DIM):
        hash_segment = int(text_hash[(i * 2) % 64:(i * 2) % 64 + 2], 16)
        embedding.append((hash_segment / 255.0) * 2 - 1)
    return embedding


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


def ensure_payload_indexes(collection):
    """Create payload indexes for efficient filtering."""
    indexes = [
        ("topic", "keyword"),
        ("perspective", "keyword"),
        ("importance", "keyword"),
        ("keywords", "keyword"),
        ("context", "keyword"),
        ("type", "keyword"),
        ("research_type", "keyword"),  # For filtering consultation vs research
    ]

    for field, field_type in indexes:
        try:
            requests.put(
                f"{QDRANT_URL}/collections/{collection}/index",
                json={
                    "field_name": field,
                    "field_schema": field_type
                }
            )
        except:
            pass  # Index might already exist


def sanitize_payload(obj):
    """Recursively sanitize strings for UTF-8 safety."""
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


# =============================================================================
# V2 FUNCTIONS (2026 Hybrid Schema)
# =============================================================================

def get_sparse_embedding(text):
    """
    Get sparse embedding for hybrid search.
    Uses local get-sparse-embedding.py module.
    """
    try:
        # Import the sparse embedding module
        from importlib.util import spec_from_file_location, module_from_spec
        sparse_path = os.path.join(SCRIPT_DIR, "get-sparse-embedding.py")

        # Handle hyphenated filename by loading as module
        spec = spec_from_file_location("sparse_embed", sparse_path)
        sparse_module = module_from_spec(spec)
        spec.loader.exec_module(sparse_module)

        indices, values = sparse_module.get_sparse_embedding(text)
        return indices, values
    except Exception as e:
        print(f"Warning: Sparse embedding failed: {e}", file=sys.stderr)
        return None, None


def store_point_v2(collection, point_id, dense_vector, sparse_indices, sparse_values, payload):
    """Store a single point with named vectors (V2 schema)."""
    url = f"{QDRANT_URL}/collections/{collection}/points"

    vector_data = {"dense": dense_vector}
    if sparse_indices is not None and sparse_values is not None:
        vector_data["sparse"] = {
            "indices": sparse_indices,
            "values": sparse_values
        }

    data = {
        "points": [{
            "id": point_id,
            "vector": vector_data,
            "payload": sanitize_payload(payload)
        }]
    }

    response = requests.put(url, json=data, headers={"Content-Type": "application/json"})
    return response.json()


def store_points_batch_v2(collection, points):
    """
    Store multiple points with named vectors (V2 schema).

    Args:
        collection: Qdrant collection name
        points: List of dicts with 'id', 'dense', 'sparse_indices', 'sparse_values', 'payload'

    Returns:
        API response dict
    """
    url = f"{QDRANT_URL}/collections/{collection}/points"

    formatted_points = []
    for p in points:
        vector_data = {"dense": p["dense"]}
        if p.get("sparse_indices") is not None and p.get("sparse_values") is not None:
            vector_data["sparse"] = {
                "indices": p["sparse_indices"],
                "values": p["sparse_values"]
            }

        formatted_points.append({
            "id": p["id"],
            "vector": vector_data,
            "payload": sanitize_payload(p["payload"])
        })

    data = {"points": formatted_points}

    response = requests.put(url, json=data, headers={"Content-Type": "application/json"})
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Store Gemini's self-chunked research output")
    parser.add_argument("--collection", default="universal_vault", help="Qdrant collection (ignored if --hybrid)")
    parser.add_argument("--session", default="Unknown", help="Session name for attribution")
    parser.add_argument("--input-file", "-i", help="Read input from file instead of stdin (for Windows compatibility)")
    parser.add_argument("--hybrid", action="store_true", help="Use V2 schema with hybrid vectors (stores to universal_vault)")
    parser.add_argument("--validate", action="store_true", help="Validate input against schema before storing")

    args = parser.parse_args()

    # V2 mode uses universal_vault collection
    collection = V2_COLLECTION if args.hybrid else args.collection

    # Read Gemini's JSON output (file or stdin)
    try:
        if args.input_file:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                input_text = f.read().strip()
        else:
            input_text = sys.stdin.read().strip()

        if not input_text:
            print(json.dumps({"error": "No input received", "hint": "On Windows, use --input-file instead of pipe"}))
            sys.exit(1)

        cleaned_text = clean_gemini_output(input_text)
        data = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}", "input_preview": input_text[:200] if input_text else "empty"}))
        sys.exit(1)

    if not data:
        print(json.dumps({"error": "No input received"}))
        sys.exit(1)

    # Validate structure
    if "chunks" not in data:
        print(json.dumps({"error": "Missing 'chunks' array in input"}))
        sys.exit(1)

    # Ensure collection and indexes exist (V2 collection pre-created during migration)
    if not args.hybrid:
        ensure_collection_exists(collection)
        ensure_payload_indexes(collection)

    # Extract metadata
    meta = data.get("meta", {})
    summary = data.get("summary", {})
    chunks = data.get("chunks", [])

    topic = meta.get("topic", "unknown")
    perspective = meta.get("perspective", "unknown")
    context = meta.get("context", "general")
    depth = meta.get("depth", "comprehensive")
    timestamp = int(datetime.now().timestamp())

    # Generate parent ID
    parent_id = str(uuid.uuid4())

    # Store summary/parent record
    # Handle both string and dict formats for summary
    if isinstance(summary, str):
        summary_text = summary
        summary_keywords = meta.get("keywords", [])
    else:
        summary_text = summary.get("text", f"Research on {topic} from {perspective} perspective")
        summary_keywords = summary.get("keywords", [])

    summary_embedding = get_ollama_embedding(summary_text)
    if not summary_embedding:
        summary_embedding = get_hash_embedding(summary_text)

    # Extract consultation-specific fields
    research_type = meta.get("research_type", "knowledge_retrieval")
    implementation_plan = data.get("implementation_plan")
    primary_recommendation = summary.get("primary_recommendation") if isinstance(summary, dict) else None

    summary_payload = {
        "type": "summary",
        "text": summary_text,
        "topic": topic,
        "perspective": perspective,
        "context": context,
        "depth": depth,
        "keywords": summary_keywords,
        "chunk_count": len(chunks),
        "total_words": meta.get("total_words", 0),
        "timestamp": timestamp,
        "session": args.session,
        "child_ids": [],  # Will be populated below
        "embedding_source": "ollama",
        "research_type": research_type,
    }

    # Add consultation-specific fields if present
    if primary_recommendation:
        summary_payload["primary_recommendation"] = primary_recommendation
    if implementation_plan:
        summary_payload["implementation_plan"] = implementation_plan

    # Build all chunk points for batch storage
    chunk_ids = []
    stored_chunks = []
    points_to_store = []

    # PHASE 1: Prepare all chunks and collect texts for batch embedding
    chunk_data = []  # Store processed chunk info
    embed_texts = []  # Texts to embed in parallel

    for i, chunk in enumerate(chunks):
        chunk_uuid = str(uuid.uuid4())

        # Handle both dict and string chunk formats
        if isinstance(chunk, str):
            # Gemini sometimes returns chunks as plain strings
            chunk = {
                "id": f"chunk-{i:02d}",
                "title": f"Section {i+1}",
                "content": chunk,
                "keywords": [],
                "questions_answered": [],
                "related_chunks": [],
                "importance": "supporting",
                "action_items": []
            }

        chunk_id = chunk.get("id", f"chunk-{i:02d}")
        content = chunk.get("content", "")
        title = chunk.get("title", f"Section {i+1}")
        keywords = chunk.get("keywords", [])
        questions = chunk.get("questions_answered", [])
        related = chunk.get("related_chunks", [])
        importance = chunk.get("importance", "supporting")
        action_items = chunk.get("action_items", [])  # For consultation chunks

        word_count = len(content.split())

        # Combine title + content for better embedding
        embed_text = f"{title}\n\n{content}"
        embed_texts.append(embed_text)

        # Store chunk data for later
        chunk_data.append({
            "uuid": chunk_uuid,
            "chunk_id": chunk_id,
            "title": title,
            "content": content,
            "keywords": keywords,
            "questions": questions,
            "related": related,
            "importance": importance,
            "action_items": action_items,
            "word_count": word_count,
            "embed_text": embed_text
        })

    # PHASE 2: Batch embed all texts in parallel (16-32x faster)
    embeddings = get_ollama_embeddings_batch(embed_texts)

    # PHASE 3: Build points with embeddings
    for i, cd in enumerate(chunk_data):
        embedding = embeddings[i] if i < len(embeddings) else None
        if not embedding:
            print(f"Warning: Using hash fallback for chunk {i}", file=sys.stderr)
            embedding = get_hash_embedding(cd["embed_text"])

        # Get sparse embedding for hybrid mode
        sparse_indices, sparse_values = None, None
        if args.hybrid:
            sparse_indices, sparse_values = get_sparse_embedding(cd["embed_text"])

        chunk_payload = {
            "type": "chunk",
            "chunk_id": cd["chunk_id"],
            "title": cd["title"],
            "text": cd["content"],
            "topic": topic,
            "perspective": perspective,
            "context": context,
            "keywords": cd["keywords"],
            "questions_answered": cd["questions"],
            "related_chunks": cd["related"],
            "importance": cd["importance"],
            "chunk_index": i,
            "total_chunks": len(chunks),
            "word_count": cd["word_count"],
            "parent_id": parent_id,
            "timestamp": timestamp,
            "session": args.session,
            "embedding_source": "ollama" if embeddings[i] else "hash",
            "research_type": research_type,
        }

        # Add consultation-specific fields if present
        if cd["action_items"]:
            chunk_payload["action_items"] = cd["action_items"]

        # Add content_type for V2 schema filtering
        if args.hybrid:
            chunk_payload["content_type"] = research_type if research_type != "knowledge_retrieval" else "research"

        # Build point structure based on schema version
        if args.hybrid:
            points_to_store.append({
                "id": cd["uuid"],
                "dense": embedding,
                "sparse_indices": sparse_indices,
                "sparse_values": sparse_values,
                "payload": chunk_payload
            })
        else:
            points_to_store.append({
                "id": cd["uuid"],
                "vector": embedding,
                "payload": chunk_payload
            })

        chunk_ids.append(cd["uuid"])
        stored_chunks.append({
            "id": cd["uuid"],
            "chunk_id": cd["chunk_id"],
            "title": cd["title"],
            "words": cd["word_count"],
            "importance": cd["importance"]
        })

    # Batch store all chunks in single API call
    if points_to_store:
        if args.hybrid:
            result = store_points_batch_v2(collection, points_to_store)
        else:
            result = store_points_batch(collection, points_to_store)
        if result.get("status") != "ok":
            print(f"Warning: Batch store issue: {result}", file=sys.stderr)

    # Update summary with child_ids and store
    summary_payload["child_ids"] = chunk_ids
    if args.hybrid:
        summary_payload["content_type"] = research_type if research_type != "knowledge_retrieval" else "research"
        summary_sparse_indices, summary_sparse_values = get_sparse_embedding(summary_text)
        store_point_v2(collection, parent_id, summary_embedding, summary_sparse_indices, summary_sparse_values, summary_payload)
    else:
        store_point(collection, parent_id, summary_embedding, summary_payload)

    # Output result
    result = {
        "success": True,
        "parent_id": parent_id,
        "topic": topic,
        "perspective": perspective,
        "context": context,
        "depth": depth,
        "collection": collection,
        "session": args.session,
        "schema_version": "2.0" if args.hybrid else "1.0",
        "hybrid_vectors": args.hybrid,
        "summary_words": len(summary_text.split()),
        "chunks_stored": len(chunk_ids),
        "total_words": meta.get("total_words", sum(c["words"] for c in stored_chunks)),
        "chunks": stored_chunks
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
