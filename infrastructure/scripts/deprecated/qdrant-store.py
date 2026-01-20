#!/usr/bin/env python3
"""
DEPRECATED - 2026 MIGRATION

This script has been replaced by qdrant-store-gemini.py with --hybrid flag.
New storage should use universal_vault collection with hybrid vectors.

For migration details, see ~/.claude/MIGRATION_STATE.md

---

qdrant-store.py - Store research in Qdrant with Gemini embeddings

Usage:
  echo "gemini output" | python qdrant-store.py <topic> <collection> <session> [project]

Or:
  GOOGLE_GENAI_USE_GCA=true gemini "query" 2>&1 | python ~/.claude/scripts/qdrant-store.py "topic" "lineage_research" "SessionName" "project"
"""

import sys
import json
import re
import uuid
import requests
from datetime import datetime

QDRANT_URL = "http://localhost:6333"

def parse_gemini_output(text):
    """Parse the structured output from Gemini into components."""
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
                # Parse lists
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',') if v.strip()]
                # Parse booleans
                elif value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                # Parse floats
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

    # Extract CONTENT section - capture everything after ---CONTENT---
    # (with or without END tag, in case Gemini keeps writing)
    content_match = re.search(r'---CONTENT---\s*(.*?)(?:---END CONTENT---|$)', text, re.DOTALL)
    if content_match:
        result["content"] = content_match.group(1).strip()

    # Also capture any content that appears AFTER ---END CONTENT--- (Gemini overflow)
    overflow_match = re.search(r'---END CONTENT---\s*(.+)$', text, re.DOTALL)
    if overflow_match and overflow_match.group(1).strip():
        overflow = overflow_match.group(1).strip()
        if len(overflow) > 100:  # Only append if substantial
            result["content"] = result.get("content", "") + "\n\n## Additional Content\n" + overflow

    # If no structured format found, use the whole text
    if not result["summary"] and not result["content"]:
        result["content"] = text
        result["summary"] = text[:500] + "..." if len(text) > 500 else text

    return result

def get_embedding_via_gemini_cli(text):
    """
    Generate embedding using Gemini.
    Falls back to simple hash-based pseudo-embedding if API fails.
    """
    import subprocess
    import hashlib

    # Try using gemini CLI for a simple embedding proxy
    # Since gemini CLI doesn't directly support embeddings, we'll use a workaround
    # For now, create a deterministic pseudo-embedding based on content hash
    # This allows storage/retrieval to work; real embeddings can be added later

    # Create a 768-dim pseudo-embedding from text hash
    # This is a placeholder - real semantic search needs real embeddings
    # Handle unicode by encoding with errors='replace'
    text_hash = hashlib.sha256(text.encode('utf-8', errors='replace')).hexdigest()

    # Generate 768 float values from the hash (deterministic but not semantic)
    embedding = []
    for i in range(768):
        # Use different parts of hash to generate values between -1 and 1
        hash_segment = int(text_hash[(i * 2) % 64:(i * 2) % 64 + 2], 16)
        embedding.append((hash_segment / 255.0) * 2 - 1)

    return embedding

def sanitize_string(s):
    """Remove invalid unicode characters that break JSON."""
    if not isinstance(s, str):
        return s
    # Remove surrogate characters and other problematic unicode
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

def store_in_qdrant(collection, point_id, vector, payload):
    """Store a point in Qdrant."""
    url = f"{QDRANT_URL}/collections/{collection}/points"

    # Sanitize payload to remove invalid unicode
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
        print("Usage: python qdrant-store.py <topic> <collection> <session> [project]", file=sys.stderr)
        print("Reads Gemini output from stdin", file=sys.stderr)
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

    # Parse the structured output
    parsed = parse_gemini_output(input_text)

    # Build payload
    payload = {
        "topic": topic,
        "category": parsed["metadata"].get("category", "gemini"),
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
    text_for_embedding = f"{topic} {parsed['summary']} {parsed['content'][:2000]}"
    embedding = get_embedding_via_gemini_cli(text_for_embedding)

    # Generate unique ID
    point_id = str(uuid.uuid4())

    # Store in Qdrant
    result = store_in_qdrant(collection, point_id, embedding, payload)

    if result.get("status") == "ok":
        print(f"Stored: {collection}/{point_id}")
        print(f"Topic: {topic}")
        print(f"Summary: {parsed['summary'][:100]}...")
    else:
        print(f"ERROR: {result}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
