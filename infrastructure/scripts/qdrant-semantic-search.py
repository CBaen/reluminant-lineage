#!/usr/bin/env python3
"""
qdrant-semantic-search.py - Semantic search with rich metadata display

Finds documents by MEANING, not just keywords. Displays all metadata from
Gemini's self-chunked research output.

SCHEMA VERSION: Supports both V1 (legacy) and V2 (2026 hybrid) schemas.
- V1: Single dense vector search
- V2: Hybrid search (dense + sparse) with RRF fusion

Usage:
  python qdrant-semantic-search.py --collection <name> --query "your query"

Examples:
  # Hybrid search (recommended - uses universal_vault)
  python qdrant-semantic-search.py --hybrid --query "how does caching work"

  # Basic search (default collection is universal_vault)
  python qdrant-semantic-search.py --query "how does caching work"

  # Show only core concepts
  python qdrant-semantic-search.py --hybrid --query "caching" --importance core

  # Filter by keywords
  python qdrant-semantic-search.py --hybrid --query "caching" --keywords "write-through"

  # Show full content and questions answered
  python qdrant-semantic-search.py --hybrid --query "caching" --full

Options:
  --collection   Collection to search (ignored if --hybrid)
  --query        Natural language query (required)
  --hybrid       Use V2 hybrid search with dense + sparse vectors
  --limit        Number of results (default: 5)
  --threshold    Minimum similarity score 0-1 (default: 0.5)
  --importance   Filter: core, supporting, advanced
  --keywords     Filter: comma-separated keywords to match
  --full         Show full content, keywords, questions
  --json         Output as JSON
  --compact      Minimal output (title + score only)

Requires: ollama pull nomic-embed-text
"""

import argparse
import json
import os
import requests
import sys

# Add scripts directory to path for local imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_DIM = 768
V2_COLLECTION = "universal_vault"  # 2026 migration target


class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'


def get_ollama_embedding(text, model="nomic-embed-text"):
    """Get embedding from local Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": model, "prompt": text[:8000]},
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("embedding", [])
    except Exception as e:
        print(f"{Colors.RED}Ollama error: {e}{Colors.END}", file=sys.stderr)
    return None


def get_hash_embedding(text):
    """Fallback hash embedding."""
    import hashlib
    text_hash = hashlib.sha256(text.encode('utf-8', errors='replace')).hexdigest()
    embedding = []
    for i in range(EMBEDDING_DIM):
        hash_segment = int(text_hash[(i * 2) % 64:(i * 2) % 64 + 2], 16)
        embedding.append((hash_segment / 255.0) * 2 - 1)
    return embedding


def build_filter(importance=None, keywords=None):
    """Build Qdrant filter from options."""
    must_conditions = []

    if importance:
        must_conditions.append({
            "key": "importance",
            "match": {"value": importance}
        })

    if keywords:
        # Match any of the provided keywords
        keyword_list = [k.strip().lower() for k in keywords.split(",")]
        must_conditions.append({
            "key": "keywords",
            "match": {"any": keyword_list}
        })

    if must_conditions:
        return {"must": must_conditions}
    return None


def semantic_search(collection, query_embedding, limit=5, threshold=0.5, filter_dict=None):
    """Search Qdrant using vector similarity with optional filters (V1 schema)."""
    request_body = {
        "vector": query_embedding,
        "limit": limit,
        "score_threshold": threshold,
        "with_payload": True
    }

    if filter_dict:
        request_body["filter"] = filter_dict

    response = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/search",
        json=request_body
    )

    if response.status_code == 200:
        return response.json().get("result", [])
    return []


def get_sparse_embedding(text):
    """Get sparse embedding for hybrid search."""
    try:
        from importlib.util import spec_from_file_location, module_from_spec
        sparse_path = os.path.join(SCRIPT_DIR, "get-sparse-embedding.py")
        spec = spec_from_file_location("sparse_embed", sparse_path)
        sparse_module = module_from_spec(spec)
        spec.loader.exec_module(sparse_module)
        indices, values = sparse_module.get_sparse_embedding(text)
        return indices, values
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Sparse embedding failed: {e}{Colors.END}", file=sys.stderr)
        return None, None


def hybrid_search(collection, dense_embedding, sparse_indices=None, sparse_values=None,
                  limit=5, threshold=0.5, filter_dict=None):
    """
    Search Qdrant using hybrid vectors (V2 schema).

    Uses prefetch + RRF (Reciprocal Rank Fusion) to combine dense and sparse results.
    """
    # If no sparse vectors, fall back to dense-only search with named vectors
    if sparse_indices is None or sparse_values is None:
        request_body = {
            "vector": {
                "name": "dense",
                "vector": dense_embedding
            },
            "limit": limit,
            "score_threshold": threshold,
            "with_payload": True
        }
    else:
        # Hybrid search using prefetch + RRF fusion
        request_body = {
            "prefetch": [
                {
                    "query": dense_embedding,
                    "using": "dense",
                    "limit": limit * 3  # Over-fetch for better fusion
                },
                {
                    "query": {
                        "indices": sparse_indices,
                        "values": sparse_values
                    },
                    "using": "sparse",
                    "limit": limit * 3
                }
            ],
            "query": {"fusion": "rrf"},
            "limit": limit,
            "with_payload": True
        }

    if filter_dict:
        request_body["filter"] = filter_dict

    response = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/query",
        json=request_body
    )

    if response.status_code == 200:
        return response.json().get("result", {}).get("points", [])

    # Fallback: try the search endpoint with dense only
    print(f"{Colors.YELLOW}Hybrid query failed, falling back to dense-only{Colors.END}", file=sys.stderr)
    fallback_body = {
        "vector": {
            "name": "dense",
            "vector": dense_embedding
        },
        "limit": limit,
        "score_threshold": threshold,
        "with_payload": True
    }
    if filter_dict:
        fallback_body["filter"] = filter_dict

    response = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/search",
        json=fallback_body
    )
    if response.status_code == 200:
        return response.json().get("result", [])
    return []


def score_color(score):
    """Get color based on similarity score."""
    if score >= 0.8:
        return Colors.GREEN
    elif score >= 0.6:
        return Colors.YELLOW
    else:
        return Colors.RED


def importance_color(importance):
    """Get color based on importance level."""
    colors = {
        "core": Colors.GREEN,
        "supporting": Colors.YELLOW,
        "advanced": Colors.MAGENTA,
        "high": Colors.GREEN,
        "medium": Colors.YELLOW,
        "low": Colors.DIM
    }
    return colors.get(importance, Colors.END)


def print_result_compact(result, index):
    """Minimal output: title + score."""
    score = result.get("score", 0)
    payload = result.get("payload", {})
    title = payload.get("title", payload.get("topic", "Untitled"))
    importance = payload.get("importance", "")

    imp_badge = f"[{importance}]" if importance else ""
    print(f"  {index}. {score_color(score)}{score:.3f}{Colors.END} {title} {Colors.DIM}{imp_badge}{Colors.END}")


def print_result_standard(result, index):
    """Standard output: key metadata."""
    score = result.get("score", 0)
    payload = result.get("payload", {})

    title = payload.get("title", "Untitled")
    topic = payload.get("topic", "N/A")
    importance = payload.get("importance", "N/A")
    word_count = payload.get("word_count", 0)
    chunk_id = payload.get("chunk_id", "")

    # Get text content (try different field names)
    text = payload.get("text", payload.get("content", payload.get("summary", "")))
    preview = text[:200] + "..." if len(text) > 200 else text

    print(f"\n{Colors.BOLD}{Colors.CYAN}--- Result #{index} ---{Colors.END}")
    print(f"{Colors.BOLD}Title:{Colors.END} {title}")
    print(f"{Colors.BOLD}Score:{Colors.END} {score_color(score)}{score:.3f}{Colors.END}  "
          f"{Colors.BOLD}Importance:{Colors.END} {importance_color(importance)}{importance}{Colors.END}  "
          f"{Colors.BOLD}Words:{Colors.END} {word_count}")
    print(f"{Colors.BOLD}Topic:{Colors.END} {topic}" + (f"  {Colors.DIM}[{chunk_id}]{Colors.END}" if chunk_id else ""))

    if preview:
        print(f"\n{Colors.GREEN}{preview}{Colors.END}")


def print_result_full(result, index):
    """Full output: all metadata including questions and keywords."""
    score = result.get("score", 0)
    payload = result.get("payload", {})

    title = payload.get("title", "Untitled")
    topic = payload.get("topic", "N/A")
    perspective = payload.get("perspective", "N/A")
    importance = payload.get("importance", "N/A")
    word_count = payload.get("word_count", 0)
    chunk_id = payload.get("chunk_id", "")
    session = payload.get("session", "N/A")

    keywords = payload.get("keywords", [])
    questions = payload.get("questions_answered", [])
    related = payload.get("related_chunks", [])

    # Get text content
    text = payload.get("text", payload.get("content", payload.get("summary", "")))

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}Result #{index}: {title}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")

    # Metadata grid
    print(f"{Colors.BOLD}Score:{Colors.END} {score_color(score)}{score:.3f}{Colors.END}  |  "
          f"{Colors.BOLD}Importance:{Colors.END} {importance_color(importance)}{importance}{Colors.END}  |  "
          f"{Colors.BOLD}Words:{Colors.END} {word_count}")
    print(f"{Colors.BOLD}Topic:{Colors.END} {topic}  |  "
          f"{Colors.BOLD}Perspective:{Colors.END} {perspective}")
    print(f"{Colors.BOLD}Session:{Colors.END} {session}  |  "
          f"{Colors.BOLD}Chunk:{Colors.END} {chunk_id or 'N/A'}")

    # Keywords
    if keywords:
        kw_str = ", ".join(str(k) for k in keywords[:10])
        if len(keywords) > 10:
            kw_str += f" (+{len(keywords) - 10} more)"
        print(f"\n{Colors.BOLD}Keywords:{Colors.END} {Colors.YELLOW}{kw_str}{Colors.END}")

    # Questions answered
    if questions:
        print(f"\n{Colors.BOLD}Questions this answers:{Colors.END}")
        for q in questions[:5]:
            print(f"  {Colors.MAGENTA}-{q}{Colors.END}")
        if len(questions) > 5:
            print(f"  {Colors.DIM}(+{len(questions) - 5} more){Colors.END}")

    # Related chunks
    if related:
        print(f"\n{Colors.BOLD}Related:{Colors.END} {Colors.DIM}{', '.join(str(r) for r in related)}{Colors.END}")

    # Full content
    if text:
        print(f"\n{Colors.BOLD}Content:{Colors.END}")
        print(f"{Colors.GREEN}{text}{Colors.END}")


def main():
    parser = argparse.ArgumentParser(
        description="Semantic search in Qdrant with rich metadata",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--collection", default="universal_vault", help="Collection to search (ignored if --hybrid)")
    parser.add_argument("--query", required=True, help="Natural language query")
    parser.add_argument("--hybrid", action="store_true", help="Use V2 hybrid search (searches universal_vault)")
    parser.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--threshold", type=float, default=0.5, help="Min similarity 0-1 (default: 0.5)")
    parser.add_argument("--importance", choices=["core", "supporting", "advanced"], help="Filter by importance")
    parser.add_argument("--keywords", help="Filter by keywords (comma-separated)")
    parser.add_argument("--full", action="store_true", help="Show full content + all metadata")
    parser.add_argument("--compact", action="store_true", help="Minimal output (title + score)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # V2 mode uses universal_vault collection
    collection = V2_COLLECTION if args.hybrid else args.collection

    # Get query embedding
    if not args.json:
        print(f"{Colors.CYAN}Generating embedding for query...{Colors.END}", file=sys.stderr)

    query_embedding = get_ollama_embedding(args.query)
    if not query_embedding:
        if not args.json:
            print(f"{Colors.YELLOW}Ollama unavailable, using hash fallback{Colors.END}", file=sys.stderr)
        query_embedding = get_hash_embedding(args.query)

    # Build filter
    filter_dict = build_filter(
        importance=args.importance,
        keywords=args.keywords
    )

    # Get sparse embedding for hybrid mode
    sparse_indices, sparse_values = None, None
    if args.hybrid:
        if not args.json:
            print(f"{Colors.CYAN}Generating sparse embedding...{Colors.END}", file=sys.stderr)
        sparse_indices, sparse_values = get_sparse_embedding(args.query)

    # Search
    if args.hybrid:
        results = hybrid_search(
            collection,
            query_embedding,
            sparse_indices=sparse_indices,
            sparse_values=sparse_values,
            limit=args.limit,
            threshold=args.threshold,
            filter_dict=filter_dict
        )
    else:
        results = semantic_search(
            collection,
            query_embedding,
            limit=args.limit,
            threshold=args.threshold,
            filter_dict=filter_dict
        )

    # JSON output
    if args.json:
        print(json.dumps(results, indent=2))
        return

    # No results
    if not results:
        print(f"\n{Colors.YELLOW}No results found above threshold {args.threshold}{Colors.END}")
        if args.importance or args.keywords:
            print(f"{Colors.DIM}Filters applied: importance={args.importance}, keywords={args.keywords}{Colors.END}")
        print(f"Try lowering --threshold or broadening your query")
        return

    # Header
    mode_indicator = f" {Colors.MAGENTA}[hybrid]{Colors.END}" if args.hybrid else ""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Found {len(results)} results for:{Colors.END} {Colors.GREEN}\"{args.query}\"{Colors.END}{mode_indicator}")
    if args.hybrid:
        print(f"{Colors.DIM}Collection: {collection}{Colors.END}")
    if args.importance or args.keywords:
        filters = []
        if args.importance:
            filters.append(f"importance={args.importance}")
        if args.keywords:
            filters.append(f"keywords={args.keywords}")
        print(f"{Colors.DIM}Filters: {', '.join(filters)}{Colors.END}")

    # Print results
    for i, result in enumerate(results, 1):
        if args.compact:
            print_result_compact(result, i)
        elif args.full:
            print_result_full(result, i)
        else:
            print_result_standard(result, i)

    print(f"\n{Colors.CYAN}{'-' * 50}{Colors.END}")

    # Hint for more details
    if not args.full and not args.compact:
        print(f"{Colors.DIM}Tip: Use --full for complete content and metadata{Colors.END}")


if __name__ == "__main__":
    main()
