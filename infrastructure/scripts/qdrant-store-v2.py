#!/usr/bin/env python3
"""
qdrant-store-v2.py - Store research in Qdrant with REAL semantic embeddings

Embedding priority:
1. Ollama (local, free) - requires: ollama pull nomic-embed-text
2. Gemini API (if GOOGLE_API_KEY set)
3. Hash fallback (no semantic search, but works)

Usage:
  echo "content" | python qdrant-store-v2.py <topic> <collection> <session> [project]

Install Ollama embeddings:
  winget install ollama
  ollama pull nomic-embed-text
"""

import sys
import json
import re
import uuid
import hashlib
import subprocess
import requests
from datetime import datetime

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_DIM = 768  # nomic-embed-text dimension


def get_ollama_embedding(text, model="nomic-embed-text"):
    """Get embedding from local Ollama instance."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": model, "prompt": text[:8000]},  # Limit context
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            embedding = data.get("embedding", [])
            if embedding and len(embedding) == EMBEDDING_DIM:
                return embedding, "ollama"
    except Exception as e:
        print(f"Ollama unavailable: {e}", file=sys.stderr)
    return None, None


def get_gemini_embedding(text):
    """Get embedding from Gemini API (requires GOOGLE_API_KEY)."""
    import os
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None, None

    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent",
            params={"key": api_key},
            json={
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": text[:8000]}]},
                "taskType": "RETRIEVAL_DOCUMENT",
                "outputDimensionality": EMBEDDING_DIM
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            embedding = data.get("embedding", {}).get("values", [])
            if embedding:
                return embedding, "gemini"
    except Exception as e:
        print(f"Gemini API unavailable: {e}", file=sys.stderr)
    return None, None


def get_hash_embedding(text):
    """Fallback: deterministic pseudo-embedding from hash (no semantic search)."""
    text_hash = hashlib.sha256(text.encode('utf-8', errors='replace')).hexdigest()
    embedding = []
    for i in range(EMBEDDING_DIM):
        hash_segment = int(text_hash[(i * 2) % 64:(i * 2) % 64 + 2], 16)
        embedding.append((hash_segment / 255.0) * 2 - 1)
    return embedding, "hash"


def get_embedding(text):
    """Get embedding with fallback chain: ollama -> gemini -> hash."""
    # Try Ollama first (local, free)
    embedding, source = get_ollama_embedding(text)
    if embedding:
        return embedding, source

    # Try Gemini API
    embedding, source = get_gemini_embedding(text)
    if embedding:
        return embedding, source

    # Fall back to hash (works but no semantic search)
    return get_hash_embedding(text)


def parse_gemini_output(text):
    """Parse structured output from Gemini into components."""
    result = {
        "metadata": {},
        "summary": "",
        "content": ""
    }

    # Extract METADATA section
    metadata_match = re.search(r'---METADATA---\s*(.*?)\s*---END METADATA---', text, re.DOTALL)
    if metadata_match:
        metadata_text = metadata_match.group(1)
        for line in metadata_text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',') if v.strip()]
                elif value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif re.match(r'^[\d.]+$', value):
                    try:
                        value = float(value)
                    except:
                        pass
                result["metadata"][key] = value

    # Extract SUMMARY section
    summary_match = re.search(r'---SUMMARY---\s*(.*?)\s*---END SUMMARY---', text, re.DOTALL)
    if summary_match:
        result["summary"] = summary_match.group(1).strip()

    # Extract CONTENT section
    content_match = re.search(r'---CONTENT---\s*(.*?)(?:---END CONTENT---|$)', text, re.DOTALL)
    if content_match:
        result["content"] = content_match.group(1).strip()

    # Capture overflow
    overflow_match = re.search(r'---END CONTENT---\s*(.+)$', text, re.DOTALL)
    if overflow_match and overflow_match.group(1).strip():
        overflow = overflow_match.group(1).strip()
        if len(overflow) > 100:
            result["content"] = result.get("content", "") + "\n\n## Additional Content\n" + overflow

    # Fallback for unstructured content
    if not result["summary"] and not result["content"]:
        result["content"] = text
        result["summary"] = text[:500] + "..." if len(text) > 500 else text

    return result


def sanitize_string(s):
    """Remove invalid unicode characters."""
    if not isinstance(s, str):
        return s
    return s.encode('utf-8', errors='replace').decode('utf-8', errors='replace')


def sanitize_payload(payload):
    """Recursively sanitize all strings in payload."""
    if isinstance(payload, dict):
        return {k: sanitize_payload(v) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    elif isinstance(payload, str):
        return sanitize_string(payload)
    return payload


def ensure_collection_exists(collection):
    """Create collection if it doesn't exist."""
    # Check if exists
    response = requests.get(f"{QDRANT_URL}/collections/{collection}")
    if response.status_code == 200:
        return True

    # Create with correct dimensions
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


def store_in_qdrant(collection, point_id, vector, payload):
    """Store a point in Qdrant."""
    url = f"{QDRANT_URL}/collections/{collection}/points"
    clean_payload = sanitize_payload(payload)

    data = {
        "points": [
            {
                "id": point_id,
                "vector": vector,
                "payload": clean_payload
            }
        ]
    }

    response = requests.put(url, json=data, headers={"Content-Type": "application/json"})
    return response.json()


def main():
    if len(sys.argv) < 4:
        print("Usage: python qdrant-store-v2.py <topic> <collection> <session> [project]", file=sys.stderr)
        print("Reads content from stdin", file=sys.stderr)
        print("\nEmbedding sources (in priority order):", file=sys.stderr)
        print("  1. Ollama (ollama pull nomic-embed-text)", file=sys.stderr)
        print("  2. Gemini API (set GOOGLE_API_KEY)", file=sys.stderr)
        print("  3. Hash fallback (no semantic search)", file=sys.stderr)
        sys.exit(1)

    topic = sys.argv[1]
    collection = sys.argv[2]
    session = sys.argv[3]
    project = sys.argv[4] if len(sys.argv) > 4 else None

    # Read from stdin
    input_text = sys.stdin.read()

    if not input_text.strip():
        print("ERROR: No input received", file=sys.stderr)
        sys.exit(1)

    # Ensure collection exists
    ensure_collection_exists(collection)

    # Parse the structured output
    parsed = parse_gemini_output(input_text)

    # Build payload
    payload = {
        "topic": topic,
        "category": parsed["metadata"].get("category", "research"),
        "tags": parsed["metadata"].get("tags", []),
        "sources": parsed["metadata"].get("sources", []),
        "confidence": parsed["metadata"].get("confidence", 0.5),
        "summary": parsed["summary"],
        "content": parsed["content"],
        "session_name": session,
        "project": project,
        "created_at": datetime.now().isoformat(),
        "continuation_needed": parsed["metadata"].get("continuation_needed", False),
        "gaps": parsed["metadata"].get("gaps", [])
    }

    # Generate embedding from summary + content
    text_for_embedding = f"{topic}\n{parsed['summary']}\n{parsed['content'][:4000]}"
    embedding, embedding_source = get_embedding(text_for_embedding)

    # Add embedding metadata
    payload["embedding_source"] = embedding_source
    payload["embedding_dim"] = len(embedding)

    # Generate unique ID
    point_id = str(uuid.uuid4())

    # Store in Qdrant
    result = store_in_qdrant(collection, point_id, embedding, payload)

    if result.get("status") == "ok":
        print(f"Stored: {collection}/{point_id}")
        print(f"Topic: {topic}")
        print(f"Embedding: {embedding_source} ({len(embedding)} dims)")
        print(f"Summary: {parsed['summary'][:100]}...")
    else:
        print(f"ERROR: {result}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
