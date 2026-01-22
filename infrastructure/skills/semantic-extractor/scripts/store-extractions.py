#!/usr/bin/env python3
"""
store-extractions.py - Store extraction results to Qdrant with Hub-and-Spoke organization

V3 Features:
- Deduplication via hash + semantic similarity
- 0.90-0.95 similarity flagged for review (may be contradictions)
- >0.95 similarity auto-merged with episode_refs update
- Scope-aware deduplication (series vs episode)

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
        flagged/                <- V3: Items flagged for human review (0.90-0.95 similarity)

Usage:
    python store-extractions.py --save-extraction results.json    # Save extraction to hub
    python store-extractions.py --store-episode 2                 # Store episode to Qdrant
    python store-extractions.py --store-all                       # Store all pending episodes
    python store-extractions.py --status                          # Show index summary
    python store-extractions.py --cleanup                         # Delete 30+ day archives
    python store-extractions.py --check-duplicate "text"          # V3: Check if text exists
    python store-extractions.py --review-flagged                  # V3: Show flagged items
"""

import argparse
import hashlib
import json
import re
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
FLAGGED_DIR = EXTRACTIONS_DIR / "flagged"  # V3: Items needing human review
INDEX_FILE = EXTRACTIONS_DIR / "index.json"

# V3: Deduplication thresholds
SIMILARITY_AUTO_MERGE = 0.95  # Above this: auto-merge as duplicate
SIMILARITY_FLAG_REVIEW = 0.90  # Between 0.90-0.95: flag for review (may be contradiction)

# V3: Content types that should be deduplicated series-wide
SERIES_SCOPE_TYPES = [
    "lore_fact",
    "historical_fact",
    "used_imagery",  # with scope=series
    "used_sensory_language",  # with scope=series
    "forbidden_conclusion",
    "revelation",
]

# V3: Content types that are episode-specific (can repeat per episode)
EPISODE_SCOPE_TYPES = [
    "character_state",
    "episode_term_usage",
]


def ensure_directories():
    """Create extraction directories if they don't exist."""
    EPISODES_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVED_DIR.mkdir(parents=True, exist_ok=True)
    FLAGGED_DIR.mkdir(parents=True, exist_ok=True)


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
# V3: DEDUPLICATION
# =============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for hashing: lowercase, strip, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def compute_text_hash(text: str) -> str:
    """Compute SHA256 hash of normalized text."""
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def should_deduplicate(extraction: dict) -> bool:
    """
    Determine if this extraction should be checked for duplicates.

    Series-scope types are always deduplicated.
    Episode-scope types can repeat per episode.
    """
    content_type = extraction.get("content_type", "")
    scope = extraction.get("scope", "series")  # Default to series

    # Episode-specific types don't get deduplicated
    if content_type in EPISODE_SCOPE_TYPES:
        return False

    # Series-scope types always deduplicate
    if content_type in SERIES_SCOPE_TYPES:
        # But check scope for imagery/sensory - episode scope can repeat
        if content_type in ["used_imagery", "used_sensory_language"]:
            return scope == "series"
        return True

    # Relationships deduplicate series-wide
    if content_type == "relationship":
        return True

    # Default: deduplicate
    return True


def check_hash_duplicate(text_hash: str) -> dict | None:
    """
    Check if exact hash exists in Qdrant.

    Returns the existing point if found, None otherwise.
    """
    try:
        response = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION}/points/scroll",
            json={
                "filter": {
                    "must": [
                        {"key": "text_hash", "match": {"value": text_hash}}
                    ]
                },
                "limit": 1,
                "with_payload": True,
                "with_vector": False
            },
            timeout=30
        )

        if response.status_code == 200:
            points = response.json().get("result", {}).get("points", [])
            if points:
                return points[0]
        return None
    except Exception as e:
        print(f"[WARN] Hash check failed: {e}", file=sys.stderr)
        return None


def check_semantic_duplicate(text: str, content_type: str) -> tuple[dict | None, float]:
    """
    Check for semantic duplicates using vector similarity.

    Returns (existing_point, similarity_score) or (None, 0.0).
    """
    try:
        # Get embedding for the new text
        embed_text = text[:8000]
        embedding = get_embedding(embed_text)
        if embedding is None:
            return None, 0.0

        # Search for similar items of the same content type
        response = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
            json={
                "vector": {"name": "dense", "vector": embedding},
                "filter": {
                    "must": [
                        {"key": "content_type", "match": {"value": content_type}}
                    ]
                },
                "limit": 1,
                "with_payload": True,
                "score_threshold": SIMILARITY_FLAG_REVIEW  # Only return if above review threshold
            },
            timeout=30
        )

        if response.status_code == 200:
            results = response.json().get("result", [])
            if results:
                return results[0], results[0].get("score", 0.0)
        return None, 0.0
    except Exception as e:
        print(f"[WARN] Semantic check failed: {e}", file=sys.stderr)
        return None, 0.0


def update_episode_refs(point_id: str, new_episode: int) -> bool:
    """
    Add episode number to existing point's episode_refs array.

    Used when auto-merging duplicates.
    """
    try:
        # Get current point
        response = requests.get(
            f"{QDRANT_URL}/collections/{COLLECTION}/points/{point_id}",
            timeout=30
        )

        if response.status_code != 200:
            return False

        point = response.json().get("result", {})
        payload = point.get("payload", {})
        episode_refs = payload.get("episode_refs", [])

        # Add new episode if not already present
        if new_episode not in episode_refs:
            episode_refs.append(new_episode)
            episode_refs.sort()

            # Update the point
            update_response = requests.post(
                f"{QDRANT_URL}/collections/{COLLECTION}/points/payload",
                json={
                    "points": [point_id],
                    "payload": {
                        "episode_refs": episode_refs,
                        "last_updated": datetime.now().isoformat()
                    }
                },
                timeout=30
            )
            return update_response.status_code == 200

        return True  # Already has this episode
    except Exception as e:
        print(f"[WARN] Failed to update episode_refs: {e}", file=sys.stderr)
        return False


def flag_for_review(extraction: dict, existing: dict, similarity: float, episode: int):
    """
    Save an item that needs human review (0.90-0.95 similarity).

    These may be contradictions between episodes.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    flag_file = FLAGGED_DIR / f"review_{timestamp}_{uuid.uuid4().hex[:8]}.json"

    review_data = {
        "flagged_at": datetime.now().isoformat(),
        "reason": "similarity_review",
        "similarity_score": similarity,
        "new_extraction": {
            "episode": episode,
            "text": extraction.get("text"),
            "content_type": extraction.get("content_type"),
            "reasoning": extraction.get("reasoning")
        },
        "existing_item": {
            "id": existing.get("id"),
            "episode_refs": existing.get("payload", {}).get("episode_refs", []),
            "text": existing.get("payload", {}).get("text"),
            "content_type": existing.get("payload", {}).get("content_type")
        },
        "action_needed": "Review if these are duplicates or contradictions. If contradiction, both should be kept."
    }

    with open(flag_file, 'w', encoding='utf-8') as f:
        json.dump(review_data, f, indent=2)

    print(f"[FLAG] Similarity {similarity:.2f} - flagged for review: {flag_file.name}", file=sys.stderr)


def check_duplicate(extraction: dict, episode: int) -> tuple[str, dict | None]:
    """
    V3 Deduplication check.

    Returns:
        ("store", None) - No duplicate, store as new
        ("skip", existing) - Exact duplicate, skip (update episode_refs)
        ("merge", existing) - High similarity duplicate, merge
        ("flag", existing) - Medium similarity, needs human review
    """
    if not should_deduplicate(extraction):
        return "store", None

    text = extraction.get("text", "")
    content_type = extraction.get("content_type", "")

    if not text:
        return "store", None

    # Step 1: Check hash (exact match)
    text_hash = compute_text_hash(text)
    existing = check_hash_duplicate(text_hash)

    if existing:
        # Exact match - update episode_refs and skip
        point_id = existing.get("id")
        if point_id:
            update_episode_refs(point_id, episode)
        return "skip", existing

    # Step 2: Check semantic similarity
    similar, score = check_semantic_duplicate(text, content_type)

    if similar:
        if score >= SIMILARITY_AUTO_MERGE:
            # High similarity - auto-merge
            point_id = similar.get("id")
            if point_id:
                update_episode_refs(point_id, episode)
            return "merge", similar
        elif score >= SIMILARITY_FLAG_REVIEW:
            # Medium similarity - flag for review (may be contradiction)
            flag_for_review(extraction, similar, score, episode)
            return "flag", similar

    # No significant duplicate found
    return "store", None


# =============================================================================
# QDRANT STORAGE
# =============================================================================

# V3: Parallel embedding configuration
PARALLEL_WORKERS = 32  # Number of concurrent embedding requests (Ollama handles this well)
BATCH_SIZE = 50  # Number of points to upsert in one Qdrant call


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


def get_embeddings_parallel(texts: list[str]) -> list:
    """
    V3: Get embeddings for multiple texts in parallel.

    Uses ThreadPoolExecutor for concurrent Ollama requests.
    Returns list of embeddings (or None for failures) in same order as input.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = [None] * len(texts)

    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
        # Submit all embedding tasks
        future_to_idx = {
            executor.submit(get_embedding, text): idx
            for idx, text in enumerate(texts)
        }

        # Collect results as they complete
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"[ERROR] Parallel embedding {idx} failed: {e}", file=sys.stderr)
                results[idx] = None

    return results


def batch_upsert_to_qdrant(points: list) -> tuple[int, int]:
    """
    V3: Upsert multiple points to Qdrant in one call.

    Returns (success_count, failure_count).
    """
    if not points:
        return 0, 0

    try:
        response = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION}/points",
            json={"points": points},
            timeout=60
        )
        if response.status_code == 200:
            return len(points), 0
        print(f"[ERROR] Batch upsert failed: {response.text[:200]}", file=sys.stderr)
        return 0, len(points)
    except Exception as e:
        print(f"[ERROR] Batch upsert error: {e}", file=sys.stderr)
        return 0, len(points)


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


def store_extraction_to_qdrant(extraction: dict, session: str, skip_dedup: bool = False) -> tuple[str | None, str]:
    """
    Store a single extraction to Qdrant with V3 deduplication.

    Returns:
        (point_id, status) where status is one of:
        - "stored": New item stored
        - "skipped": Exact duplicate, episode_refs updated
        - "merged": High similarity duplicate, merged
        - "flagged": Medium similarity, flagged for review but still stored
        - "error": Storage failed
    """
    episode_num = extraction.get("episode_number", 0)

    # V3: Check for duplicates first
    if not skip_dedup:
        action, existing = check_duplicate(extraction, episode_num)

        if action == "skip":
            return existing.get("id") if existing else None, "skipped"
        elif action == "merge":
            return existing.get("id") if existing else None, "merged"
        elif action == "flag":
            # Flagged items are still stored (might be contradictions we want to keep)
            pass  # Continue to store

    point_id = str(uuid.uuid4())

    embed_text = f"{extraction.get('text', '')} {extraction.get('reasoning', '')}"
    dense = get_embedding(embed_text)
    if dense is None:
        return None, "error"

    sparse_indices, sparse_values = get_sparse_vector(embed_text)

    # V3: Compute text hash for deduplication index
    text_hash = compute_text_hash(extraction.get("text", ""))

    # V3: Enhanced payload with deduplication and voting fields
    payload = {
        # Core fields
        "content_type": extraction.get("content_type"),
        "title": f"Ep{episode_num} - {extraction.get('content_type')}",
        "text": extraction.get("text"),
        "reasoning": extraction.get("reasoning"),
        "confidence": extraction.get("confidence", 0.85),
        "agreement": extraction.get("agreement", "unknown"),
        "episode_number": episode_num,
        "chunk_index": extraction.get("chunk_index"),
        "timestamp": int(datetime.now().timestamp()),
        "session": session,
        "project": "wardenclyffe",
        "is_fiction": True,

        # V3: Deduplication fields
        "text_hash": text_hash,
        "episode_refs": [episode_num],  # Array for tracking across episodes
        "is_duplicate": False,

        # V3: Voting metadata
        "votes_for": extraction.get("votes_for", 0),
        "extraction_version": 3,

        # V3: Relationship fields (if relationship type)
        "entity_a": extraction.get("entity_a"),
        "entity_b": extraction.get("entity_b"),
        "relationship_type": extraction.get("relationship_type"),
        "direction": extraction.get("direction"),
        "temporal_context": extraction.get("temporal_context"),
        "evidence": extraction.get("evidence"),
        "relationship_subjects": (
            [extraction.get("entity_a"), extraction.get("entity_b")]
            if extraction.get("content_type") == "relationship"
            else None
        ),

        # V3: Scope field for sensory/imagery
        "scope": extraction.get("scope", "series"),
    }

    # Remove None values to keep payload clean
    payload = {k: v for k, v in payload.items() if v is not None}

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
            return point_id, "stored"
        print(f"[ERROR] Qdrant failed: {response.text[:200]}", file=sys.stderr)
        return None, "error"
    except Exception as e:
        print(f"[ERROR] Qdrant error: {e}", file=sys.stderr)
        return None, "error"


def store_extractions_batch(extractions: list, session: str, skip_dedup: bool = False) -> dict:
    """
    V3: Store multiple extractions with parallel embedding.

    Process:
    1. Run dedup checks sequentially (to avoid race conditions)
    2. Batch remaining items for embedding
    3. Get embeddings in parallel
    4. Batch upsert to Qdrant

    Returns stats dict: {stored, skipped, merged, flagged, error}
    """
    stats = {"stored": 0, "skipped": 0, "merged": 0, "flagged": 0, "error": 0}

    if not extractions:
        return stats

    # Step 1: Dedup check (sequential to avoid race conditions)
    to_store = []
    for ext in extractions:
        episode_num = ext.get("episode_number", 0)

        if not skip_dedup:
            action, existing = check_duplicate(ext, episode_num)
            if action == "skip":
                stats["skipped"] += 1
                continue
            elif action == "merge":
                stats["merged"] += 1
                continue
            elif action == "flag":
                stats["flagged"] += 1
                # Continue to store (might be contradiction)

        to_store.append(ext)

    if not to_store:
        return stats

    print(f"    [PARALLEL] Embedding {len(to_store)} items with {PARALLEL_WORKERS} workers...", file=sys.stderr)

    # Step 2: Prepare texts for embedding
    embed_texts = [
        f"{ext.get('text', '')} {ext.get('reasoning', '')}"
        for ext in to_store
    ]

    # Step 3: Get embeddings in parallel
    embeddings = get_embeddings_parallel(embed_texts)

    # Step 4: Build points and batch upsert
    points = []
    for i, (ext, dense) in enumerate(zip(to_store, embeddings)):
        if dense is None:
            stats["error"] += 1
            continue

        episode_num = ext.get("episode_number", 0)
        embed_text = embed_texts[i]
        sparse_indices, sparse_values = get_sparse_vector(embed_text)
        text_hash = compute_text_hash(ext.get("text", ""))
        point_id = str(uuid.uuid4())

        payload = {
            "content_type": ext.get("content_type"),
            "title": f"Ep{episode_num} - {ext.get('content_type')}",
            "text": ext.get("text"),
            "reasoning": ext.get("reasoning"),
            "confidence": ext.get("confidence", 0.85),
            "agreement": ext.get("agreement", "unknown"),
            "episode_number": episode_num,
            "chunk_index": ext.get("chunk_index"),
            "timestamp": int(datetime.now().timestamp()),
            "session": session,
            "project": "wardenclyffe",
            "is_fiction": True,
            "text_hash": text_hash,
            "episode_refs": [episode_num],
            "is_duplicate": False,
            "votes_for": ext.get("votes_for", 0),
            "extraction_version": 3,
            "entity_a": ext.get("entity_a"),
            "entity_b": ext.get("entity_b"),
            "relationship_type": ext.get("relationship_type"),
            "direction": ext.get("direction"),
            "temporal_context": ext.get("temporal_context"),
            "evidence": ext.get("evidence"),
            "relationship_subjects": (
                [ext.get("entity_a"), ext.get("entity_b")]
                if ext.get("content_type") == "relationship"
                else None
            ),
            "scope": ext.get("scope", "series"),
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        points.append({
            "id": point_id,
            "vector": {
                "dense": dense,
                "sparse": {"indices": sparse_indices, "values": sparse_values}
            },
            "payload": payload
        })

        # Batch upsert when we hit batch size
        if len(points) >= BATCH_SIZE:
            success, fail = batch_upsert_to_qdrant(points)
            stats["stored"] += success
            stats["error"] += fail
            points = []

    # Upsert remaining points
    if points:
        success, fail = batch_upsert_to_qdrant(points)
        stats["stored"] += success
        stats["error"] += fail

    return stats


def store_episode_to_qdrant(episode_num: int, skip_dedup: bool = False, use_parallel: bool = True) -> bool:
    """
    Store all pending chunks for an episode to Qdrant.

    V3: Now tracks deduplication stats (stored, skipped, merged, flagged).
    V3: use_parallel=True enables batch embedding (4x faster).
    """
    ep_dir = get_episode_dir(episode_num)

    if not ep_dir.exists():
        print(f"[ERROR] Episode {episode_num} not found", file=sys.stderr)
        return False

    manifest = load_manifest(episode_num)
    session = f"SemanticExtractor-V3-{datetime.now().strftime('%Y-%m-%d')}"

    # V3: Track all statuses
    stats = {"stored": 0, "skipped": 0, "merged": 0, "flagged": 0, "error": 0}

    for chunk_file in sorted(ep_dir.glob("chunk-*.json")):
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)

        if chunk_data.get("stored_to_qdrant"):
            print(f"[SKIP] {chunk_file.name} already stored", file=sys.stderr)
            continue

        print(f"[INFO] Storing {chunk_file.name}...", file=sys.stderr)

        extractions = chunk_data.get("extractions", [])

        # V3: Use parallel batch processing
        if use_parallel and len(extractions) > 1:
            chunk_stats = store_extractions_batch(extractions, session, skip_dedup=skip_dedup)
        else:
            # Fall back to sequential for single items
            chunk_stats = {"stored": 0, "skipped": 0, "merged": 0, "flagged": 0, "error": 0}
            for ext in extractions:
                _, status = store_extraction_to_qdrant(ext, session, skip_dedup=skip_dedup)
                chunk_stats[status] = chunk_stats.get(status, 0) + 1

        # Accumulate stats
        for key in stats:
            stats[key] += chunk_stats.get(key, 0)

        # Only errors count as failures
        if chunk_stats["error"] == 0:
            # Mark as stored
            chunk_data["stored_to_qdrant"] = True
            chunk_data["stored_at"] = datetime.now().isoformat()
            chunk_data["v3_stats"] = chunk_stats  # V3: Record dedup stats
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, indent=2)

            # Archive a copy
            archive_name = f"{datetime.now().strftime('%Y%m%d')}_ep{episode_num:03d}_{chunk_file.name}"
            shutil.copy(str(chunk_file), str(ARCHIVED_DIR / archive_name))

        print(f"  stored:{chunk_stats['stored']} skipped:{chunk_stats['skipped']} "
              f"merged:{chunk_stats['merged']} flagged:{chunk_stats['flagged']} "
              f"error:{chunk_stats['error']}", file=sys.stderr)

    # Update manifest and index
    update_manifest_stats(manifest)
    save_manifest(episode_num, manifest)

    index = load_index()
    if str(episode_num) in index.get("episodes", {}):
        index["episodes"][str(episode_num)]["status"] = manifest["status"]
        index["episodes"][str(episode_num)]["stored_count"] = manifest["stored_count"]
        index["episodes"][str(episode_num)]["pending_count"] = manifest["pending_count"]
        index["episodes"][str(episode_num)]["v3_stats"] = stats  # V3: Record dedup stats
    update_index_stats(index)
    save_index(index)

    print(f"\n[DONE] Episode {episode_num} V3 Summary:", file=sys.stderr)
    print(f"  New items stored: {stats['stored']}", file=sys.stderr)
    print(f"  Exact duplicates skipped: {stats['skipped']}", file=sys.stderr)
    print(f"  High-similarity merged: {stats['merged']}", file=sys.stderr)
    print(f"  Flagged for review: {stats['flagged']}", file=sys.stderr)
    print(f"  Errors: {stats['error']}", file=sys.stderr)

    return stats["error"] == 0


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
# V3: REVIEW FLAGGED ITEMS
# =============================================================================

def show_flagged_items():
    """Display items flagged for human review."""
    flagged_files = list(FLAGGED_DIR.glob("review_*.json"))

    if not flagged_files:
        print("\n[INFO] No items flagged for review.\n", file=sys.stderr)
        return

    print(f"\n=== FLAGGED FOR REVIEW ({len(flagged_files)} items) ===\n")

    for flag_file in sorted(flagged_files):
        with open(flag_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"File: {flag_file.name}")
        print(f"  Similarity: {data.get('similarity_score', 0):.2f}")
        print(f"  New (Ep {data.get('new_extraction', {}).get('episode')}):")
        print(f"    {data.get('new_extraction', {}).get('text', '')[:80]}...")
        print(f"  Existing (Eps {data.get('existing_item', {}).get('episode_refs', [])}):")
        print(f"    {data.get('existing_item', {}).get('text', '')[:80]}...")
        print()


def check_text_duplicate(text: str):
    """Check if a specific text would be considered a duplicate."""
    print(f"\n=== DUPLICATE CHECK ===\n", file=sys.stderr)
    print(f"Text: {text[:100]}...\n", file=sys.stderr)

    # Check hash
    text_hash = compute_text_hash(text)
    print(f"Hash: {text_hash[:16]}...", file=sys.stderr)

    existing = check_hash_duplicate(text_hash)
    if existing:
        print(f"\n[EXACT MATCH] Found in Qdrant:", file=sys.stderr)
        print(f"  ID: {existing.get('id')}", file=sys.stderr)
        print(f"  Episodes: {existing.get('payload', {}).get('episode_refs', [])}", file=sys.stderr)
        return

    # Check semantic similarity for common types
    for content_type in ["lore_fact", "historical_fact", "used_sensory_language"]:
        similar, score = check_semantic_duplicate(text, content_type)
        if similar:
            print(f"\n[SIMILAR] Found {content_type} with score {score:.2f}:", file=sys.stderr)
            print(f"  ID: {similar.get('id')}", file=sys.stderr)
            print(f"  Text: {similar.get('payload', {}).get('text', '')[:100]}...", file=sys.stderr)

            if score >= SIMILARITY_AUTO_MERGE:
                print(f"  -> Would be AUTO-MERGED", file=sys.stderr)
            elif score >= SIMILARITY_FLAG_REVIEW:
                print(f"  -> Would be FLAGGED for review", file=sys.stderr)
            return

    print("\n[NO DUPLICATE] This text would be stored as new.", file=sys.stderr)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Store extractions with hub-and-spoke organization (V3)")
    parser.add_argument("--save-extraction", "-s", metavar="FILE", help="Save extraction JSON to hub")
    parser.add_argument("--store-episode", "-e", type=int, metavar="NUM", help="Store episode to Qdrant")
    parser.add_argument("--store-all", action="store_true", help="Store all pending episodes")
    parser.add_argument("--status", action="store_true", help="Show index summary")
    parser.add_argument("--cleanup", action="store_true", help="Delete old archived files")

    # V3: New options
    parser.add_argument("--check-duplicate", metavar="TEXT", help="V3: Check if text is a duplicate")
    parser.add_argument("--review-flagged", action="store_true", help="V3: Show items flagged for review")
    parser.add_argument("--skip-dedup", action="store_true", help="V3: Skip deduplication checks")

    args = parser.parse_args()
    ensure_directories()

    if args.status:
        show_status()
    elif args.save_extraction:
        save_extraction_to_hub(Path(args.save_extraction))
    elif args.store_episode:
        store_episode_to_qdrant(args.store_episode, skip_dedup=args.skip_dedup)
    elif args.store_all:
        index = load_index()
        for ep_num in index.get("episodes", {}):
            ep_info = index["episodes"][ep_num]
            if ep_info.get("pending_count", 0) > 0:
                store_episode_to_qdrant(int(ep_num), skip_dedup=args.skip_dedup)
        cleanup_old_archives()
    elif args.cleanup:
        cleanup_old_archives()
    elif args.check_duplicate:
        check_text_duplicate(args.check_duplicate)
    elif args.review_flagged:
        show_flagged_items()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
