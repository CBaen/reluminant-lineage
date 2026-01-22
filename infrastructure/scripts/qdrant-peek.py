#!/usr/bin/env python3
"""
qdrant-peek.py - Token-efficient Qdrant retrieval

Two-stage retrieval for context conservation:
1. PEEK: Get metadata only (no text) to judge relevance
2. FETCH: Get full content for specific IDs only

Usage:
  # Stage 1: Peek at what exists (tiny output)
  python qdrant-peek.py peek --collection lineage_research --query "OAuth"

  # Stage 2: Fetch specific IDs (only what you need)
  python qdrant-peek.py fetch --collection lineage_research --ids "uuid1,uuid2"

Token savings: ~80% vs fetching everything
"""

import argparse
import json
import requests
import sys

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"

# Metadata fields to return (NOT text/content)
PEEK_FIELDS = [
    "title", "topic", "keywords", "questions_answered",
    "importance", "perspective", "word_count", "session"
]


def get_embedding(text: str) -> list:
    """Get embedding from Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text[:8000]},
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("embedding", [])
    except Exception as e:
        print(f"Ollama error: {e}", file=sys.stderr)
    return None


def peek(collection: str, query: str, limit: int = 5, threshold: float = 0.5) -> list:
    """
    Search with metadata only - no text content.
    Returns lightweight results for relevance judgment.
    """
    embedding = get_embedding(query)
    if not embedding:
        return []

    response = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/search",
        json={
            "vector": {"name": "dense", "vector": embedding},
            "limit": limit,
            "score_threshold": threshold,
            "with_payload": {
                "include": PEEK_FIELDS
            }
        }
    )

    if response.status_code == 200:
        results = response.json().get("result", [])
        # Format for minimal output
        formatted = []
        for r in results:
            p = r.get("payload", {})
            formatted.append({
                "id": r["id"],
                "score": round(r["score"], 3),
                "title": p.get("title", p.get("topic", "Untitled")),
                "keywords": p.get("keywords", [])[:5],
                "questions": p.get("questions_answered", [])[:3],
                "importance": p.get("importance", ""),
                "words": p.get("word_count", 0)
            })
        return formatted
    return []


def fetch(collection: str, ids: list) -> list:
    """
    Fetch full content for specific IDs only.
    Use after peek() to get only what you need.
    """
    response = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points",
        json={"ids": ids, "with_payload": True}
    )

    if response.status_code == 200:
        return response.json().get("result", [])
    return []


def cmd_peek(args):
    """Peek command - metadata only."""
    results = peek(args.collection, args.query, args.limit, args.threshold)

    if not results:
        print("No results found")
        return

    if args.json:
        print(json.dumps(results, indent=2))
        return

    # Compact human-readable output
    print(f"\n=== {len(results)} results for: \"{args.query}\" ===\n")
    for r in results:
        print(f"[{r['score']}] {r['title']}")
        print(f"    ID: {r['id']}")
        if r['keywords']:
            print(f"    Keywords: {', '.join(r['keywords'])}")
        if r['questions']:
            print(f"    Answers: {r['questions'][0]}")
        if r['importance']:
            print(f"    Importance: {r['importance']}, Words: {r['words']}")
        print()

    print("---")
    print(f"To fetch full content: python qdrant-peek.py fetch -c {args.collection} --ids \"<id1>,<id2>\"")


def cmd_fetch(args):
    """Fetch command - full content for specific IDs."""
    id_list = [i.strip() for i in args.ids.split(",")]
    results = fetch(args.collection, id_list)

    if not results:
        print("No results found for those IDs")
        return

    if args.json:
        print(json.dumps(results, indent=2))
        return

    # Human-readable full output
    for r in results:
        p = r.get("payload", {})
        print(f"\n{'=' * 60}")
        print(f"ID: {r['id']}")
        print(f"Title: {p.get('title', 'Untitled')}")
        print(f"Topic: {p.get('topic', 'N/A')}")
        print(f"{'=' * 60}")

        text = p.get("text", p.get("content", p.get("summary", "")))
        if text:
            print(f"\n{text}\n")


def main():
    parser = argparse.ArgumentParser(description="Token-efficient Qdrant retrieval")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # peek
    peek_parser = subparsers.add_parser("peek", help="Metadata-only search")
    peek_parser.add_argument("-c", "--collection", required=True)
    peek_parser.add_argument("-q", "--query", required=True)
    peek_parser.add_argument("-l", "--limit", type=int, default=5)
    peek_parser.add_argument("-t", "--threshold", type=float, default=0.5)
    peek_parser.add_argument("--json", action="store_true")

    # fetch
    fetch_parser = subparsers.add_parser("fetch", help="Get full content for IDs")
    fetch_parser.add_argument("-c", "--collection", required=True)
    fetch_parser.add_argument("--ids", required=True, help="Comma-separated IDs")
    fetch_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "peek":
        cmd_peek(args)
    elif args.command == "fetch":
        cmd_fetch(args)


if __name__ == "__main__":
    main()
