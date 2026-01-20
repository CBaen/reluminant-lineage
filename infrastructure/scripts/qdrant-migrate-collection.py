#!/usr/bin/env python3
"""
qdrant-migrate-collection.py - Migrate data from V1 to V2 schema

Migrates points from legacy collections (single vector) to universal_vault
(named vectors: dense + sparse).

PROCESS:
1. Scroll through source collection
2. Re-embed text content with sparse vectors
3. Store to universal_vault with named vectors
4. Track progress in MIGRATION_STATE.md

Usage:
  # Migrate a single collection
  python qdrant-migrate-collection.py --source lineage_research

  # Migrate with batch size
  python qdrant-migrate-collection.py --source lineage_research --batch 50

  # Dry run (count points only)
  python qdrant-migrate-collection.py --source lineage_research --dry-run

  # Resume from a specific offset
  python qdrant-migrate-collection.py --source lineage_research --offset "uuid-here"

Part of the Qdrant 2026 Migration.
"""

import argparse
import json
import os
import sys
from datetime import datetime
import requests

# Add scripts directory to path for local imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_DIM = 768
V2_COLLECTION = "universal_vault"


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'


def get_sparse_embedding(text):
    """Get sparse embedding using local module."""
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


def get_ollama_embedding(text, model="nomic-embed-text"):
    """Get dense embedding from Ollama."""
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


def scroll_collection(collection, limit=100, offset=None):
    """Scroll through collection points."""
    url = f"{QDRANT_URL}/collections/{collection}/points/scroll"

    params = {
        "limit": limit,
        "with_payload": True,
        "with_vector": True
    }

    if offset:
        params["offset"] = offset

    response = requests.post(url, json=params)

    if response.status_code == 200:
        result = response.json().get("result", {})
        return result.get("points", []), result.get("next_page_offset")
    return [], None


def get_collection_info(collection):
    """Get collection metadata."""
    response = requests.get(f"{QDRANT_URL}/collections/{collection}")
    if response.status_code == 200:
        return response.json().get("result", {})
    return None


def store_points_v2(points):
    """Store points to V2 collection with named vectors."""
    url = f"{QDRANT_URL}/collections/{V2_COLLECTION}/points"

    formatted_points = []
    for p in points:
        vector_data = {"dense": p["dense"]}
        if p.get("sparse_indices") and p.get("sparse_values"):
            vector_data["sparse"] = {
                "indices": p["sparse_indices"],
                "values": p["sparse_values"]
            }

        formatted_points.append({
            "id": p["id"],
            "vector": vector_data,
            "payload": p["payload"]
        })

    response = requests.put(url, json={"points": formatted_points})
    return response.json()


def get_text_for_embedding(payload):
    """Extract text content from payload for embedding."""
    # Try various field names
    text = payload.get("text", "")
    if not text:
        text = payload.get("content", "")
    if not text:
        text = payload.get("summary", "")

    # Add title if available
    title = payload.get("title", "")
    if title and text:
        text = f"{title}\n\n{text}"

    return text


def migrate_batch(points, source_collection, dry_run=False):
    """Migrate a batch of points."""
    if dry_run:
        return {"status": "dry_run", "count": len(points)}

    migrated = []
    errors = []

    for point in points:
        point_id = point.get("id")
        payload = point.get("payload", {})
        original_vector = point.get("vector", [])

        # Get text for sparse embedding
        text = get_text_for_embedding(payload)

        if not text:
            errors.append({"id": point_id, "error": "no text content"})
            continue

        # Get sparse embedding
        sparse_indices, sparse_values = get_sparse_embedding(text)

        # Use original dense vector if available, otherwise re-embed
        if original_vector and len(original_vector) == EMBEDDING_DIM:
            dense_vector = original_vector
        else:
            dense_vector = get_ollama_embedding(text)
            if not dense_vector:
                errors.append({"id": point_id, "error": "failed to get dense embedding"})
                continue

        # Add source collection to payload for tracking
        payload["migrated_from"] = source_collection
        payload["migration_timestamp"] = int(datetime.now().timestamp())

        # Ensure content_type is set
        if "content_type" not in payload:
            # Infer from source collection or default to research
            if "consult" in source_collection:
                payload["content_type"] = "consult"
            elif "episode" in source_collection or "tesla" in source_collection:
                payload["content_type"] = "episode"
            elif "code" in source_collection:
                payload["content_type"] = "code"
            else:
                payload["content_type"] = "research"

        migrated.append({
            "id": point_id,
            "dense": dense_vector,
            "sparse_indices": sparse_indices,
            "sparse_values": sparse_values,
            "payload": payload
        })

    # Store batch
    if migrated:
        result = store_points_v2(migrated)
        if result.get("status") != "ok":
            return {"status": "error", "error": result, "migrated": 0, "errors": len(errors)}

    return {
        "status": "ok",
        "migrated": len(migrated),
        "errors": len(errors),
        "error_details": errors[:5]  # First 5 errors
    }


def main():
    parser = argparse.ArgumentParser(description="Migrate V1 collection to V2 schema")
    parser.add_argument("--source", required=True, help="Source collection to migrate")
    parser.add_argument("--batch", type=int, default=50, help="Batch size (default: 50)")
    parser.add_argument("--offset", help="Resume from this point ID")
    parser.add_argument("--dry-run", action="store_true", help="Count points only, don't migrate")
    parser.add_argument("--limit", type=int, help="Max points to migrate (for testing)")

    args = parser.parse_args()

    # Check source collection exists
    info = get_collection_info(args.source)
    if not info:
        print(f"{Colors.RED}Error: Collection '{args.source}' not found{Colors.END}")
        sys.exit(1)

    total_points = info.get("points_count", 0)
    print(f"\n{Colors.BOLD}Migration: {args.source} -> {V2_COLLECTION}{Colors.END}")
    print(f"Total points: {total_points}")
    print(f"Batch size: {args.batch}")
    if args.dry_run:
        print(f"{Colors.YELLOW}DRY RUN - no data will be migrated{Colors.END}")
    print()

    # Check V2 collection exists
    v2_info = get_collection_info(V2_COLLECTION)
    if not v2_info:
        print(f"{Colors.RED}Error: Target collection '{V2_COLLECTION}' not found{Colors.END}")
        print("Create it first with the 2026 schema")
        sys.exit(1)

    # Start migration
    migrated_total = 0
    errors_total = 0
    offset = args.offset
    batch_num = 0

    while True:
        batch_num += 1

        # Check limit
        if args.limit and migrated_total >= args.limit:
            print(f"\n{Colors.YELLOW}Reached limit of {args.limit} points{Colors.END}")
            break

        # Scroll source collection
        points, next_offset = scroll_collection(args.source, args.batch, offset)

        if not points:
            break

        print(f"Batch {batch_num}: {len(points)} points...", end=" ", flush=True)

        # Migrate batch
        result = migrate_batch(points, args.source, args.dry_run)

        if result["status"] == "dry_run":
            print(f"{Colors.DIM}[dry run]{Colors.END}")
            migrated_total += len(points)
        elif result["status"] == "ok":
            print(f"{Colors.GREEN}OK{Colors.END} ({result['migrated']} migrated, {result['errors']} errors)")
            migrated_total += result["migrated"]
            errors_total += result["errors"]
        else:
            print(f"{Colors.RED}ERROR: {result.get('error')}{Colors.END}")
            errors_total += len(points)

        # Next page
        offset = next_offset
        if not offset:
            break

    # Summary
    print(f"\n{Colors.BOLD}{'=' * 50}{Colors.END}")
    print(f"{Colors.BOLD}Migration Complete{Colors.END}")
    print(f"Source: {args.source}")
    print(f"Target: {V2_COLLECTION}")
    print(f"Migrated: {Colors.GREEN}{migrated_total}{Colors.END}")
    print(f"Errors: {Colors.RED if errors_total else Colors.DIM}{errors_total}{Colors.END}")

    if args.dry_run:
        print(f"\n{Colors.YELLOW}This was a dry run. Run without --dry-run to migrate.{Colors.END}")


if __name__ == "__main__":
    main()
