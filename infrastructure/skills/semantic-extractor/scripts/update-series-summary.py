#!/usr/bin/env python3
"""
update-series-summary.py - Update series_summary in Qdrant after each episode

Creates/updates a single series_summary entry that tracks:
- Total episodes completed
- All characters introduced
- All locked lore facts
- All open mysteries
- Sensory vocabulary used (for anti-cloning)
- Continuity locks

Usage:
    python update-series-summary.py --episode 2
    python update-series-summary.py --rebuild  # Rebuild from all episodes
"""

import argparse
import json
import os
import sys
import hashlib
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

# Config
QDRANT_URL = "http://localhost:6333"
COLLECTION = "tesla_mandela_effects"

def get_client():
    return QdrantClient(url=QDRANT_URL)

def get_all_episodes(client) -> list[int]:
    """Get list of all episode numbers in the collection."""
    results = client.scroll(
        collection_name=COLLECTION,
        scroll_filter=Filter(
            must=[FieldCondition(key="content_type", match=MatchValue(value="episode_parent"))]
        ),
        limit=1000,
        with_payload=True
    )
    episodes = set()
    for point in results[0]:
        ep_num = point.payload.get("episode_number")
        if ep_num:
            episodes.add(int(ep_num))
    return sorted(episodes)

def get_episode_extractions(client, episode_number: int) -> dict:
    """Get all extractions for an episode, grouped by content_type."""
    results = client.scroll(
        collection_name=COLLECTION,
        scroll_filter=Filter(
            must=[FieldCondition(key="episode_number", match=MatchValue(value=episode_number))]
        ),
        limit=10000,
        with_payload=True
    )

    by_type = {}
    for point in results[0]:
        content_type = point.payload.get("content_type", "unknown")
        if content_type not in by_type:
            by_type[content_type] = []
        by_type[content_type].append(point.payload)

    return by_type

def extract_characters(extractions: dict) -> list[str]:
    """Extract all character names from extractions."""
    characters = set()

    # From character_state
    for item in extractions.get("character_state", []):
        chars = item.get("characters", [])
        if isinstance(chars, list):
            characters.update(chars)

    # From relationships
    for item in extractions.get("relationship", []):
        entity_a = item.get("entity_a", "")
        entity_b = item.get("entity_b", "")
        # Only add if they look like character names (not concepts)
        if entity_a and not any(x in entity_a.lower() for x in ["grid", "geometry", "light", "sun"]):
            characters.add(entity_a)
        if entity_b and not any(x in entity_b.lower() for x in ["grid", "geometry", "light", "sun"]):
            characters.add(entity_b)

    # From episode_parent
    for item in extractions.get("episode_parent", []):
        chars = item.get("characters", [])
        if isinstance(chars, list):
            characters.update(chars)

    return sorted(characters)

def extract_lore_facts(extractions: dict) -> list[dict]:
    """Extract all lore_fact entries as continuity locks."""
    lore = []
    for item in extractions.get("lore_fact", []):
        lore.append({
            "text": item.get("text", ""),
            "episode": item.get("episode_number"),
            "importance": item.get("importance", "supporting")
        })
    return lore

def extract_mysteries(extractions: dict) -> list[dict]:
    """Extract open_mystery and proposed_question entries."""
    mysteries = []
    for item in extractions.get("open_mystery", []):
        mysteries.append({
            "text": item.get("text", ""),
            "episode": item.get("episode_number"),
            "type": "open_mystery"
        })
    for item in extractions.get("proposed_question", []):
        mysteries.append({
            "text": item.get("text", ""),
            "episode": item.get("episode_number"),
            "type": "proposed_question"
        })
    return mysteries

def extract_forbidden(extractions: dict) -> list[dict]:
    """Extract forbidden_conclusion entries."""
    forbidden = []
    for item in extractions.get("forbidden_conclusion", []):
        forbidden.append({
            "text": item.get("text", ""),
            "episode": item.get("episode_number")
        })
    return forbidden

def extract_sensory(extractions: dict) -> list[dict]:
    """Extract used_sensory_language entries."""
    sensory = []
    for item in extractions.get("used_sensory_language", []):
        sensory.append({
            "text": item.get("text", ""),
            "episode": item.get("episode_number"),
            "sensory_type": item.get("sensory_type", "unknown")
        })
    return sensory

def build_series_summary(client, up_to_episode: int = None) -> dict:
    """Build complete series summary from all episodes."""
    episodes = get_all_episodes(client)

    if up_to_episode:
        episodes = [e for e in episodes if e <= up_to_episode]

    if not episodes:
        print("[WARN] No episodes found in collection", file=sys.stderr)
        return None

    all_characters = set()
    all_lore = []
    all_mysteries = []
    all_forbidden = []
    all_sensory = []

    for ep_num in episodes:
        print(f"[INFO] Processing Episode {ep_num}...", file=sys.stderr)
        extractions = get_episode_extractions(client, ep_num)

        all_characters.update(extract_characters(extractions))
        all_lore.extend(extract_lore_facts(extractions))
        all_mysteries.extend(extract_mysteries(extractions))
        all_forbidden.extend(extract_forbidden(extractions))
        all_sensory.extend(extract_sensory(extractions))

    # Build summary text
    summary_text = f"""Series Summary (through Episode {max(episodes)})

Episodes Completed: {len(episodes)}
Total Characters: {len(all_characters)}
Lore Facts Established: {len(all_lore)}
Open Mysteries: {len([m for m in all_mysteries if m['type'] == 'open_mystery'])}
Proposed Questions: {len([m for m in all_mysteries if m['type'] == 'proposed_question'])}
Forbidden Conclusions: {len(all_forbidden)}
Sensory Phrases Used: {len(all_sensory)}

Key Characters: {', '.join(sorted(all_characters)[:20])}{'...' if len(all_characters) > 20 else ''}
"""

    return {
        "content_type": "series_summary",
        "title": f"Series Summary (through Episode {max(episodes)})",
        "text": summary_text,
        "episodes_completed": len(episodes),
        "episode_numbers": episodes,
        "characters": sorted(all_characters),
        "lore_facts_count": len(all_lore),
        "mysteries_count": len(all_mysteries),
        "forbidden_count": len(all_forbidden),
        "sensory_count": len(all_sensory),
        "keywords": ["series", "summary", "continuity", "lore", "characters"],
        "importance": "core",
        "timestamp": datetime.now().isoformat(),
        "session": os.environ.get("USER", "unknown"),
        "project": "wardenclyffe"
    }

def get_embedding(text: str) -> list[float]:
    """Get embedding from Ollama."""
    import subprocess
    import json

    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/embeddings",
             "-d", json.dumps({"model": "nomic-embed-text", "prompt": text[:2000]})],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("embedding", [0.0] * 768)
    except Exception as e:
        print(f"[WARN] Embedding failed: {e}", file=sys.stderr)

    return [0.0] * 768

def store_series_summary(client, summary: dict):
    """Store or update series_summary in Qdrant."""
    # Generate deterministic ID for series_summary
    summary_id = "series-summary-main"
    point_id = int(hashlib.md5(summary_id.encode()).hexdigest()[:12], 16)

    # Get embedding
    embedding = get_embedding(summary["text"])

    # Delete existing if present
    try:
        client.delete(
            collection_name=COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="content_type", match=MatchValue(value="series_summary"))]
            )
        )
    except Exception:
        pass

    # Store new
    client.upsert(
        collection_name=COLLECTION,
        points=[PointStruct(
            id=point_id,
            vector={"dense": embedding},
            payload=summary
        )]
    )

    print(f"[OK] Series summary stored (ID: {point_id})", file=sys.stderr)
    return point_id

def main():
    parser = argparse.ArgumentParser(description="Update series summary in Qdrant")
    parser.add_argument("--episode", "-e", type=int, help="Update through this episode number")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild from all episodes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be stored")

    args = parser.parse_args()

    client = get_client()

    # Build summary
    summary = build_series_summary(client, args.episode)

    if not summary:
        print("[ERROR] Could not build series summary", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return

    # Store
    store_series_summary(client, summary)

    print(f"\n[DONE] Series summary updated through Episode {summary['episodes_completed']}")
    print(f"  Characters: {len(summary['characters'])}")
    print(f"  Lore facts: {summary['lore_facts_count']}")
    print(f"  Mysteries: {summary['mysteries_count']}")

if __name__ == "__main__":
    main()
