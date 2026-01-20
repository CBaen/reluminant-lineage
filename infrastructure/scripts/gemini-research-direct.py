#!/usr/bin/env python3
"""
gemini-research-direct.py - Gemini researches AND stores directly to Qdrant

Architecture: Gemini does ALL heavy lifting, returns only COORDINATES to caller
- No data flows through Claude's context
- Subagent becomes lightweight coordinator
- Claude gets point_ids to retrieve later when needed

Usage:
    python gemini-research-direct.py --topic "OAuth2 authentication" --collection universal_vault --account 1

NOTE: This script uses V1 schema (single vectors). For hybrid search support,
use gemini-research-store.py with qdrant-store-gemini.py --hybrid instead.

Returns JSON:
    {
        "success": true,
        "collection": "lineage_research",
        "point_ids": ["uuid1", "uuid2", ...],
        "chunk_count": 8,
        "total_words": 2500,
        "topic": "OAuth2 authentication"
    }

Claude gets COORDINATES only, not the research data.
"""

import argparse
import subprocess
import sys
import os
import json
import uuid
import tempfile
import requests
from pathlib import Path
from datetime import datetime


# Configuration
QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"


def get_script_dir():
    return Path(__file__).parent.resolve()


def find_git_bash():
    """Find Git Bash on Windows."""
    candidates = [
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files\Git\bin\bash.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return "bash"


def call_gemini(account: int, prompt: str, model: str = "gemini-2.0-flash") -> str:
    """Call Gemini via gemini-account.sh."""
    script_path = get_script_dir() / "gemini-account.sh"

    if sys.platform == "win32":
        bash_path = find_git_bash()
        cmd = [bash_path, str(script_path), str(account), prompt, model]
    else:
        cmd = ["bash", str(script_path), str(account), prompt, model]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.stdout


def get_embedding(text: str) -> list:
    """Get embedding from Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=30
        )
        return response.json().get("embedding", [])
    except Exception as e:
        print(f"Embedding error: {e}", file=sys.stderr)
        return [0.0] * 768  # Return zero vector on error


def store_to_qdrant(collection: str, points: list) -> list:
    """Store points to Qdrant, return point IDs."""
    try:
        response = requests.put(
            f"{QDRANT_URL}/collections/{collection}/points",
            json={"points": points},
            timeout=30
        )
        if response.status_code == 200:
            return [p["id"] for p in points]
        else:
            print(f"Qdrant error: {response.text}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Qdrant connection error: {e}", file=sys.stderr)
        return []


def ensure_collection(collection: str):
    """Ensure Qdrant collection exists."""
    try:
        # Check if exists
        response = requests.get(f"{QDRANT_URL}/collections/{collection}")
        if response.status_code == 200:
            return True

        # Create collection
        requests.put(
            f"{QDRANT_URL}/collections/{collection}",
            json={
                "vectors": {"size": 768, "distance": "Cosine"}
            }
        )
        return True
    except Exception as e:
        print(f"Collection setup error: {e}", file=sys.stderr)
        return False


def clean_gemini_output(text: str) -> str:
    """Clean Gemini output of common artifacts."""
    # Remove "Loaded cached credentials." prefix
    if "Loaded cached credentials." in text:
        text = text.split("Loaded cached credentials.", 1)[-1].strip()

    # Remove markdown code blocks
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def research_and_store(topic: str, collection: str, account: int, perspective: str = "general") -> dict:
    """
    Main function: Gemini researches, chunks, and stores directly.
    Returns only COORDINATES, not the data.
    """

    # Ensure collection exists
    if not ensure_collection(collection):
        return {"success": False, "error": "Failed to ensure collection"}

    # Build research prompt with chunking instructions
    prompt = f'''DO NOT use any tools. DO NOT wrap output in markdown code blocks.

You are a research expert preparing data for vector database storage.

RESEARCH TOPIC: {topic}
PERSPECTIVE: {perspective}

OUTPUT: Return ONLY valid JSON with this exact structure:

{{
  "meta": {{
    "topic": "{topic}",
    "perspective": "{perspective}",
    "total_words": <integer>,
    "chunk_count": <integer>,
    "generated_at": "{datetime.now().isoformat()}"
  }},
  "summary": {{
    "text": "2-4 sentence overview",
    "keywords": ["key", "words"]
  }},
  "chunks": [
    {{
      "id": "chunk-01",
      "title": "Clear Searchable Title",
      "content": "200-400 words explaining ONE concept",
      "keywords": ["specific", "keywords"],
      "importance": "core"
    }}
  ]
}}

CHUNKING RULES:
- Each chunk = ONE concept (200-400 words)
- Create 6-12 chunks for comprehensive coverage
- importance: core (fundamental), supporting (examples), advanced (edge cases)

Return ONLY valid JSON, no other text.'''

    # Call Gemini
    raw_output = call_gemini(account, prompt)
    cleaned = clean_gemini_output(raw_output)

    # Parse JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"JSON parse error: {e}",
            "raw_preview": cleaned[:500]
        }

    # Validate structure
    if "chunks" not in data or not data["chunks"]:
        return {
            "success": False,
            "error": "No chunks in response",
            "raw_preview": cleaned[:500]
        }

    # Generate embeddings and prepare Qdrant points
    points = []
    session = f"direct-{datetime.now().strftime('%Y-%m-%d-%H%M')}"

    for chunk in data["chunks"]:
        point_id = str(uuid.uuid4())

        # Generate embedding from content
        embedding = get_embedding(chunk.get("content", ""))

        # Build Qdrant point
        point = {
            "id": point_id,
            "vector": embedding,
            "payload": {
                "type": "chunk",
                "topic": topic,
                "perspective": perspective,
                "title": chunk.get("title", ""),
                "text": chunk.get("content", ""),
                "keywords": chunk.get("keywords", []),
                "importance": chunk.get("importance", "supporting"),
                "session": session,
                "timestamp": int(datetime.now().timestamp()),
                "source": "gemini-research-direct"
            }
        }
        points.append(point)

    # Store to Qdrant
    point_ids = store_to_qdrant(collection, points)

    if not point_ids:
        return {
            "success": False,
            "error": "Failed to store to Qdrant"
        }

    # Return COORDINATES only - not the data
    return {
        "success": True,
        "collection": collection,
        "point_ids": point_ids,
        "chunk_count": len(point_ids),
        "total_words": data.get("meta", {}).get("total_words", 0),
        "topic": topic,
        "session": session
    }


def main():
    parser = argparse.ArgumentParser(description="Gemini research direct to Qdrant")
    parser.add_argument("--topic", "-t", required=True, help="Research topic")
    parser.add_argument("--collection", "-c", default="universal_vault", help="Qdrant collection (default: universal_vault)")
    parser.add_argument("--account", "-a", type=int, default=1, choices=[1, 2], help="Gemini account")
    parser.add_argument("--perspective", "-p", default="general", help="Research perspective")

    args = parser.parse_args()

    result = research_and_store(
        topic=args.topic,
        collection=args.collection,
        account=args.account,
        perspective=args.perspective
    )

    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
