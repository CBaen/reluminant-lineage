#!/usr/bin/env python3
"""
reset-collection.py - Manage tesla_mandela_effects collection with V3 schema

Backs up existing data before reset, recreates with proper indexes.

Usage:
    python reset-collection.py --status              # Show current state
    python reset-collection.py --backup              # Backup to dated JSON
    python reset-collection.py --reset               # Full reset (backup + recreate)
    python reset-collection.py --reset --no-backup   # Reset without backup (DANGEROUS)
    python reset-collection.py --create-indexes      # Just create missing indexes
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import requests

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION = "tesla_mandela_effects"

# Directories
SKILL_DIR = Path(__file__).parent.parent
BACKUPS_DIR = SKILL_DIR / "backups"

# V3 Collection Configuration
COLLECTION_CONFIG = {
    "vectors": {
        "dense": {
            "size": 768,
            "distance": "Cosine"
        },
        "sparse": {
            "index": {
                "on_disk": False
            }
        }
    },
    "sparse_vectors": {
        "sparse": {}
    }
}

# Payload indexes to create
PAYLOAD_INDEXES = [
    # Keyword indexes (exact match)
    {"field_name": "content_type", "field_schema": "keyword"},
    {"field_name": "text_hash", "field_schema": "keyword"},
    {"field_name": "sensory_type", "field_schema": "keyword"},
    {"field_name": "scope", "field_schema": "keyword"},
    {"field_name": "is_duplicate", "field_schema": "bool"},
    {"field_name": "is_fiction", "field_schema": "bool"},
    {"field_name": "is_resolved", "field_schema": "bool"},
    {"field_name": "must_not_resolve", "field_schema": "bool"},

    # Integer indexes (range queries)
    {"field_name": "episode_number", "field_schema": "integer"},
    {"field_name": "first_episode", "field_schema": "integer"},
    {"field_name": "chunk_index", "field_schema": "integer"},
    {"field_name": "timestamp", "field_schema": "integer"},

    # Text indexes (array fields for filtering)
    {"field_name": "relationship_subjects", "field_schema": {"type": "keyword", "is_array": True}},
    {"field_name": "characters", "field_schema": {"type": "keyword", "is_array": True}},
    {"field_name": "subjects", "field_schema": {"type": "keyword", "is_array": True}},
    {"field_name": "keywords", "field_schema": {"type": "keyword", "is_array": True}},
]


def ensure_directories():
    """Create backup directory if needed."""
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def get_collection_info() -> dict | None:
    """Get collection info from Qdrant."""
    try:
        response = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}", timeout=10)
        if response.status_code == 200:
            return response.json().get("result")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get collection info: {e}", file=sys.stderr)
        return None


def get_all_points() -> list:
    """Retrieve all points from collection using scroll."""
    points = []
    offset = None

    try:
        while True:
            payload = {"limit": 100, "with_payload": True, "with_vector": False}
            if offset:
                payload["offset"] = offset

            response = requests.post(
                f"{QDRANT_URL}/collections/{COLLECTION}/points/scroll",
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                print(f"[ERROR] Scroll failed: {response.text}", file=sys.stderr)
                break

            result = response.json().get("result", {})
            batch = result.get("points", [])
            points.extend(batch)

            offset = result.get("next_page_offset")
            if not offset or not batch:
                break

        return points
    except Exception as e:
        print(f"[ERROR] Failed to scroll points: {e}", file=sys.stderr)
        return []


def show_status():
    """Display collection status."""
    info = get_collection_info()

    print("\n=== COLLECTION STATUS ===\n")

    if info is None:
        print(f"Collection '{COLLECTION}' does not exist.")
        return

    print(f"Collection: {COLLECTION}")
    print(f"Points: {info.get('points_count', 0)}")
    print(f"Vectors: {info.get('vectors_count', 0)}")
    print(f"Status: {info.get('status', 'unknown')}")

    # Show vector config
    vectors_config = info.get("config", {}).get("params", {}).get("vectors", {})
    print(f"\nVector Config:")
    for name, config in vectors_config.items():
        if isinstance(config, dict):
            print(f"  {name}: size={config.get('size', '?')}, distance={config.get('distance', '?')}")

    # Show indexes
    payload_schema = info.get("payload_schema", {})
    if payload_schema:
        print(f"\nPayload Indexes ({len(payload_schema)}):")
        for field, schema in sorted(payload_schema.items()):
            print(f"  {field}: {schema.get('data_type', schema)}")
    else:
        print("\nNo payload indexes configured.")

    # Show content type distribution
    try:
        response = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION}/points/scroll",
            json={"limit": 1000, "with_payload": True, "with_vector": False},
            timeout=30
        )
        if response.status_code == 200:
            points = response.json().get("result", {}).get("points", [])
            if points:
                type_counts = {}
                for p in points:
                    ctype = p.get("payload", {}).get("content_type", "unknown")
                    type_counts[ctype] = type_counts.get(ctype, 0) + 1

                print(f"\nContent Type Distribution:")
                for ctype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                    print(f"  {ctype}: {count}")
    except Exception:
        pass

    print()


def backup_collection() -> Path | None:
    """Backup all points to dated JSON file."""
    ensure_directories()

    info = get_collection_info()
    if info is None:
        print(f"[WARN] Collection '{COLLECTION}' does not exist, nothing to backup.", file=sys.stderr)
        return None

    points_count = info.get("points_count", 0)
    if points_count == 0:
        print("[WARN] Collection is empty, nothing to backup.", file=sys.stderr)
        return None

    print(f"[INFO] Backing up {points_count} points...", file=sys.stderr)

    points = get_all_points()

    if not points:
        print("[ERROR] Failed to retrieve points for backup.", file=sys.stderr)
        return None

    # Create backup file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUPS_DIR / f"backup_{COLLECTION}_{timestamp}.json"

    backup_data = {
        "collection": COLLECTION,
        "timestamp": datetime.now().isoformat(),
        "points_count": len(points),
        "points": [
            {
                "id": p.get("id"),
                "payload": p.get("payload")
            }
            for p in points
        ]
    }

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2)

    print(f"[OK] Backed up {len(points)} points to {backup_file}", file=sys.stderr)
    return backup_file


def delete_collection() -> bool:
    """Delete the collection."""
    try:
        response = requests.delete(f"{QDRANT_URL}/collections/{COLLECTION}", timeout=30)
        if response.status_code == 200:
            print(f"[OK] Deleted collection '{COLLECTION}'", file=sys.stderr)
            return True
        elif response.status_code == 404:
            print(f"[INFO] Collection '{COLLECTION}' already does not exist", file=sys.stderr)
            return True
        else:
            print(f"[ERROR] Failed to delete: {response.text}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"[ERROR] Delete failed: {e}", file=sys.stderr)
        return False


def create_collection() -> bool:
    """Create collection with V3 schema."""
    try:
        # Create with hybrid vectors
        response = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION}",
            json={
                "vectors": {
                    "dense": {
                        "size": 768,
                        "distance": "Cosine"
                    }
                },
                "sparse_vectors": {
                    "sparse": {}
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            print(f"[OK] Created collection '{COLLECTION}' with hybrid vectors", file=sys.stderr)
            return True
        else:
            print(f"[ERROR] Failed to create collection: {response.text}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"[ERROR] Create failed: {e}", file=sys.stderr)
        return False


def create_indexes() -> int:
    """Create payload indexes. Returns count of indexes created."""
    created = 0

    for index_config in PAYLOAD_INDEXES:
        field_name = index_config["field_name"]
        field_schema = index_config["field_schema"]

        try:
            # Handle array fields
            if isinstance(field_schema, dict):
                payload = {"field_name": field_name, "field_schema": field_schema}
            else:
                payload = {"field_name": field_name, "field_schema": field_schema}

            response = requests.put(
                f"{QDRANT_URL}/collections/{COLLECTION}/index",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                print(f"[OK] Created index: {field_name}", file=sys.stderr)
                created += 1
            else:
                # Index might already exist
                if "already exists" in response.text.lower():
                    print(f"[SKIP] Index already exists: {field_name}", file=sys.stderr)
                else:
                    print(f"[WARN] Failed to create index {field_name}: {response.text}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Index creation failed for {field_name}: {e}", file=sys.stderr)

    return created


def reset_collection(skip_backup: bool = False) -> bool:
    """Full reset: backup -> delete -> create -> index."""

    # Step 1: Backup (unless skipped)
    if not skip_backup:
        backup_file = backup_collection()
        if backup_file:
            print(f"[INFO] Backup saved to: {backup_file}", file=sys.stderr)
    else:
        print("[WARN] Skipping backup as requested", file=sys.stderr)

    # Step 2: Delete
    if not delete_collection():
        return False

    # Step 3: Create
    if not create_collection():
        return False

    # Step 4: Create indexes
    created = create_indexes()
    print(f"[INFO] Created {created}/{len(PAYLOAD_INDEXES)} indexes", file=sys.stderr)

    print(f"\n[DONE] Collection '{COLLECTION}' reset with V3 schema", file=sys.stderr)
    return True


def main():
    parser = argparse.ArgumentParser(description="Manage tesla_mandela_effects collection")
    parser.add_argument("--status", action="store_true", help="Show collection status")
    parser.add_argument("--backup", action="store_true", help="Backup collection to JSON")
    parser.add_argument("--reset", action="store_true", help="Full reset (backup + recreate)")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup during reset")
    parser.add_argument("--create-indexes", action="store_true", help="Create missing indexes")

    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.backup:
        backup_collection()
    elif args.reset:
        reset_collection(skip_backup=args.no_backup)
    elif args.create_indexes:
        created = create_indexes()
        print(f"[DONE] Created {created} indexes", file=sys.stderr)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
