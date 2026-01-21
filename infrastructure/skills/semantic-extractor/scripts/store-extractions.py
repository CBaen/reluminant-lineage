#!/usr/bin/env python3
"""
store-extractions.py - Store extraction results to Qdrant with Hub-and-Spoke organization

Directory structure:
    extractions/
        index.json              <- Master index: all episodes, overall stats
        episodes/
            002/
                manifest.json   <- Episode status, chunk count, dates
                chunk-01.json   <- Individual chunk extractions
                chunk-02.json
            003/
                manifest.json
                ...
        archived/               <- 30-day retention of successfully stored files

Usage:
    python store-extractions.py --save-extraction results.json    # Save extraction to hub
    python store-extractions.py --store-episode 2                 # Store episode to Qdrant
    python store-extractions.py --store-all                       # Store all pending episodes
    python store-extractions.py --status                          # Show index summary
    python store-extractions.py --cleanup                         # Delete 30+ day archives
"""

import argparse
import json
import shutil
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import requests

# Configuration
QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
COLLECTION = "tesla_mandela_effects"
RETENTION_DAYS = 30

# Directories
SKILL_DIR = Path(__file__).parent.parent
EXTRACTIONS_DIR = SKILL_DIR / "extractions"
EPISODES_DIR = EXTRACTIONS_DIR / "episodes"
ARCHIVED_DIR = EXTRACTIONS_DIR / "archived"
INDEX_FILE = EXTRACTIONS_DIR / "index.json"


def ensure_directories():
    """Create extraction directories if they don't exist."""
    EPISODES_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVED_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# INDEX MANAGEMENT
# =============================================================================

def load_index() -> dict:
    """Load or create the master index."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "statistics": {
            "total_episodes": 0,
            "total_extractions": 0,
            "stored_to_qdrant": 0,
            "pending_storage": 0,
            "by_content_type": {}
        },
        "episodes": {}
    }


def save_index(index: dict):
    """Save the master index."""
    index["last_updated"] = datetime.now().isoformat()
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)


def update_index_stats(index: dict):
    """Recalculate index statistics from episode manifests."""
    stats = {
        "total_episodes": 0,
        "total_extractions": 0,
        "stored_to_qdrant": 0,
        "pending_storage": 0,
        "by_content_type": {}
    }

    for ep_num, ep_info in index["episodes"].items():
        stats["total_episodes"] += 1
        stats["total_extractions"] += ep_info.get("total_extractions", 0)
        stats["stored_to_qdrant"] += ep_info.get("stored_count", 0)
        stats["pending_storage"] += ep_info.get("pending_count", 0)

        for ctype, count in ep_info.get("by_content_type", {}).items():
            stats["by_content_type"][ctype] = stats["by_content_type"].get(ctype, 0) + count

    index["statistics"] = stats


# =============================================================================
# EPISODE MANIFEST MANAGEMENT
# =============================================================================

def get_episode_dir(episode_num: int) -> Path:
    """Get the directory for an episode."""
    return EPISODES_DIR / f"{episode_num:03d}"


def load_manifest(episode_num: int) -> dict:
    """Load or create an episode manifest."""
    ep_dir = get_episode_dir(episode_num)
    manifest_file = ep_dir / "manifest.json"

    if manifest_file.exists():
        with open(manifest_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {
        "episode_number": episode_num,
        "episode_title": f"Episode {episode_num}",
        "created": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "status": "pending",  # pending, processing, stored, needs_review
        "chunks": {},
        "total_extractions": 0,
        "stored_count": 0,
        "pending_count": 0,
        "by_content_type": {}
    }


def save_manifest(episode_num: int, manifest: dict):
    """Save an episode manifest."""
    ep_dir = get_episode_dir(episode_num)
    ep_dir.mkdir(parents=True, exist_ok=True)

    manifest["last_updated"] = datetime.now().isoformat()
    manifest_file = ep_dir / "manifest.json"

    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)


def update_manifest_stats(manifest: dict):
    """Recalculate manifest statistics from chunk files."""
    ep_dir = get_episode_dir(manifest["episode_number"])

    total = 0
    stored = 0
    pending = 0
    by_type = {}

    for chunk_file in ep_dir.glob("chunk-*.json"):
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)

        extractions = chunk_data.get("extractions", [])
        chunk_stored = chunk_data.get("stored_to_qdrant", False)

        total += len(extractions)
        if chunk_stored:
            stored += len(extractions)
        else:
            pending += len(extractions)

        for ext in extractions:
            ctype = ext.get("content_type", "unknown")
            by_type[ctype] = by_type.get(ctype, 0) + 1

    manifest["total_extractions"] = total
    manifest["stored_count"] = stored
    manifest["pending_count"] = pending
    manifest["by_content_type"] = by_type

    # Update status
    if pending == 0 and total > 0:
        manifest["status"] = "stored"
    elif stored > 0:
        manifest["status"] = "partial"
    else:
        manifest["status"] = "pending"


# =============================================================================
# SAVE EXTRACTION TO HUB
# =============================================================================

def save_extraction_to_hub(extraction_file: Path) -> bool:
    """Save an extraction JSON to the hub-and-spoke structure."""
    try:
        with open(extraction_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read {extraction_file}: {e}", file=sys.stderr)
        return False

    episode_num = data.get("episode")
    chunk_index = data.get("chunk_index")

    if episode_num is None or chunk_index is None:
        print("[ERROR] Extraction missing episode or chunk_index", file=sys.stderr)
        return False

    # Save chunk file
    ep_dir = get_episode_dir(episode_num)
    ep_dir.mkdir(parents=True, exist_ok=True)

    chunk_file = ep_dir / f"chunk-{chunk_index:02d}.json"
    data["stored_to_qdrant"] = False
    data["saved_at"] = datetime.now().isoformat()

    with open(chunk_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"[OK] Saved Episode {episode_num} Chunk {chunk_index} -> {chunk_file.name}", file=sys.stderr)

    # Update manifest
    manifest = load_manifest(episode_num)
    manifest["chunks"][str(chunk_index)] = {
        "file": chunk_file.name,
        "extraction_count": len(data.get("extractions", [])),
        "needs_opus": data.get("needs_opus_review", 0),
        "stored": False
    }
    update_manifest_stats(manifest)
    save_manifest(episode_num, manifest)

    # Update index
    index = load_index()
    index["episodes"][str(episode_num)] = {
        "episode_number": episode_num,
        "title": manifest.get("episode_title", f"Episode {episode_num}"),
        "status": manifest["status"],
        "total_extractions": manifest["total_extractions"],
        "stored_count": manifest["stored_count"],
        "pending_count": manifest["pending_count"],
        "by_content_type": manifest["by_content_type"],
        "last_updated": datetime.now().isoformat()
    }
    update_index_stats(index)
    save_index(index)

    return True


# =============================================================================
# QDRANT STORAGE
# =============================================================================

def get_embedding(text: str):
    """Get embedding from Ollama nomic-embed-text."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text[:8000]},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["embedding"]
        print(f"[ERROR] Embedding failed: {response.text}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] Embedding error: {e}", file=sys.stderr)
        return None


def get_sparse_vector(text: str) -> tuple:
    """Generate TF-IDF-like sparse vector."""
    words = text.lower().split()
    word_counts = {}
    for word in words:
        word = ''.join(c for c in word if c.isalnum())
        if word and len(word) > 2:
            word_counts[word] = word_counts.get(word, 0) + 1

    index_to_value = {}
    for word, count in word_counts.items():
        idx = abs(hash(word)) % 100000
        index_to_value[idx] = index_to_value.get(idx, 0) + float(count)

    return list(index_to_value.keys()), list(index_to_value.values())


def store_extraction_to_qdrant(extraction: dict, session: str):
    """Store a single extraction to Qdrant. Returns point_id or None."""
    point_id = str(uuid.uuid4())

    embed_text = f"{extraction.get('text', '')} {extraction.get('reasoning', '')}"
    dense = get_embedding(embed_text)
    if dense is None:
        return None

    sparse_indices, sparse_values = get_sparse_vector(embed_text)

    payload = {
        "content_type": extraction.get("content_type"),
        "title": f"Ep{extraction.get('episode_number')} - {extraction.get('content_type')}",
        "text": extraction.get("text"),
        "reasoning": extraction.get("reasoning"),
        "confidence": extraction.get("confidence", 0.85),
        "agreement": extraction.get("agreement", "unknown"),
        "episode_number": extraction.get("episode_number"),
        "chunk_index": extraction.get("chunk_index"),
        "timestamp": int(datetime.now().timestamp()),
        "session": session,
        "project": "wardenclyffe",
        "is_fiction": True,
    }

    point = {
        "id": point_id,
        "vector": {
            "dense": dense,
            "sparse": {"indices": sparse_indices, "values": sparse_values}
        },
        "payload": payload
    }

    try:
        response = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION}/points",
            json={"points": [point]},
            timeout=30
        )
        if response.status_code == 200:
            return point_id
        print(f"[ERROR] Qdrant failed: {response.text[:200]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] Qdrant error: {e}", file=sys.stderr)
        return None


def store_episode_to_qdrant(episode_num: int) -> bool:
    """Store all pending chunks for an episode to Qdrant."""
    ep_dir = get_episode_dir(episode_num)

    if not ep_dir.exists():
        print(f"[ERROR] Episode {episode_num} not found", file=sys.stderr)
        return False

    manifest = load_manifest(episode_num)
    session = f"SemanticExtractor-{datetime.now().strftime('%Y-%m-%d')}"

    total_stored = 0
    total_failed = 0

    for chunk_file in sorted(ep_dir.glob("chunk-*.json")):
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)

        if chunk_data.get("stored_to_qdrant"):
            print(f"[SKIP] {chunk_file.name} already stored", file=sys.stderr)
            continue

        print(f"[INFO] Storing {chunk_file.name}...", file=sys.stderr)

        stored = 0
        failed = 0

        for ext in chunk_data.get("extractions", []):
            point_id = store_extraction_to_qdrant(ext, session)
            if point_id:
                stored += 1
            else:
                failed += 1

        if failed == 0:
            # Mark as stored
            chunk_data["stored_to_qdrant"] = True
            chunk_data["stored_at"] = datetime.now().isoformat()
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, indent=2)

            # Archive a copy
            archive_name = f"{datetime.now().strftime('%Y%m%d')}_ep{episode_num:03d}_{chunk_file.name}"
            shutil.copy(str(chunk_file), str(ARCHIVED_DIR / archive_name))

        total_stored += stored
        total_failed += failed
        print(f"  {stored} stored, {failed} failed", file=sys.stderr)

    # Update manifest and index
    update_manifest_stats(manifest)
    save_manifest(episode_num, manifest)

    index = load_index()
    index["episodes"][str(episode_num)]["status"] = manifest["status"]
    index["episodes"][str(episode_num)]["stored_count"] = manifest["stored_count"]
    index["episodes"][str(episode_num)]["pending_count"] = manifest["pending_count"]
    update_index_stats(index)
    save_index(index)

    print(f"[DONE] Episode {episode_num}: {total_stored} stored, {total_failed} failed", file=sys.stderr)
    return total_failed == 0


# =============================================================================
# STATUS & CLEANUP
# =============================================================================

def show_status():
    """Display index summary."""
    index = load_index()
    stats = index.get("statistics", {})

    print("\n=== SEMANTIC EXTRACTION INDEX ===\n")
    print(f"Episodes:     {stats.get('total_episodes', 0)}")
    print(f"Extractions:  {stats.get('total_extractions', 0)}")
    print(f"  Stored:     {stats.get('stored_to_qdrant', 0)}")
    print(f"  Pending:    {stats.get('pending_storage', 0)}")
    print(f"\nBy Content Type:")
    for ctype, count in sorted(stats.get("by_content_type", {}).items()):
        print(f"  {ctype}: {count}")

    print(f"\nEpisodes:")
    for ep_num, ep_info in sorted(index.get("episodes", {}).items(), key=lambda x: int(x[0])):
        status = ep_info.get("status", "unknown")
        total = ep_info.get("total_extractions", 0)
        stored = ep_info.get("stored_count", 0)
        print(f"  {ep_num}: {status} ({stored}/{total} stored)")

    print()


def cleanup_old_archives():
    """Delete archived files older than RETENTION_DAYS."""
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    deleted = 0

    for filepath in ARCHIVED_DIR.glob("*.json"):
        try:
            date_str = filepath.name[:8]
            file_date = datetime.strptime(date_str, "%Y%m%d")
            if file_date < cutoff:
                filepath.unlink()
                deleted += 1
                print(f"[CLEANUP] Deleted {filepath.name}", file=sys.stderr)
        except (ValueError, IndexError):
            continue

    print(f"[CLEANUP] Deleted {deleted} old archive files", file=sys.stderr)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Store extractions with hub-and-spoke organization")
    parser.add_argument("--save-extraction", "-s", metavar="FILE", help="Save extraction JSON to hub")
    parser.add_argument("--store-episode", "-e", type=int, metavar="NUM", help="Store episode to Qdrant")
    parser.add_argument("--store-all", action="store_true", help="Store all pending episodes")
    parser.add_argument("--status", action="store_true", help="Show index summary")
    parser.add_argument("--cleanup", action="store_true", help="Delete old archived files")

    args = parser.parse_args()
    ensure_directories()

    if args.status:
        show_status()
    elif args.save_extraction:
        save_extraction_to_hub(Path(args.save_extraction))
    elif args.store_episode:
        store_episode_to_qdrant(args.store_episode)
    elif args.store_all:
        index = load_index()
        for ep_num in index.get("episodes", {}):
            ep_info = index["episodes"][ep_num]
            if ep_info.get("pending_count", 0) > 0:
                store_episode_to_qdrant(int(ep_num))
        cleanup_old_archives()
    elif args.cleanup:
        cleanup_old_archives()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
