#!/usr/bin/env python3
"""
sensory-vocabulary.py - Track and manage sensory language usage across episodes

V3 Feature: Prevents "sensory cloning" by tracking distinctive phrases.
Imagery becomes eligible for reuse after 50 episodes (decay rule).

Usage:
    python sensory-vocabulary.py --check "metallic tang of ozone"    # Check if phrase is used
    python sensory-vocabulary.py --add "arterial red" --episode 3    # Add new usage
    python sensory-vocabulary.py --sync --episode 2                  # Sync from episode extractions
    python sensory-vocabulary.py --status                            # Show vocabulary stats
    python sensory-vocabulary.py --available --episode 50            # Show phrases available for reuse
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
DECAY_EPISODES = 50  # Phrases eligible for reuse after this many episodes

# Paths
SKILL_DIR = Path(__file__).parent.parent
VOCAB_FILE = SKILL_DIR / "sensory_vocabulary.json"
EXTRACTIONS_DIR = SKILL_DIR / "extractions"
EPISODES_DIR = EXTRACTIONS_DIR / "episodes"


def load_vocabulary() -> dict:
    """Load the sensory vocabulary from file."""
    if VOCAB_FILE.exists():
        with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "3.0",
        "description": "Tracks sensory language usage across episodes",
        "decay_episodes": DECAY_EPISODES,
        "last_updated": None,
        "vocabulary": {
            "visual": {},
            "auditory": {},
            "tactile": {},
            "olfactory": {},
            "gustatory": {},
            "kinesthetic": {}
        }
    }


def save_vocabulary(vocab: dict):
    """Save the sensory vocabulary to file."""
    vocab["last_updated"] = datetime.now().isoformat()
    with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, indent=2)


def normalize_phrase(phrase: str) -> str:
    """Normalize a phrase for comparison."""
    return phrase.lower().strip()


def classify_sensory_type(phrase: str) -> str:
    """
    Attempt to classify the sensory type of a phrase.
    Falls back to 'visual' as default.
    """
    phrase_lower = phrase.lower()

    # Auditory keywords
    if any(word in phrase_lower for word in ['sound', 'hear', 'whisper', 'roar', 'silence', 'echo', 'hum', 'crack', 'thunder']):
        return 'auditory'

    # Tactile keywords
    if any(word in phrase_lower for word in ['touch', 'feel', 'cold', 'warm', 'soft', 'rough', 'smooth', 'sharp', 'pressure']):
        return 'tactile'

    # Olfactory keywords
    if any(word in phrase_lower for word in ['smell', 'scent', 'odor', 'fragrance', 'stench', 'aroma', 'tang', 'musk']):
        return 'olfactory'

    # Gustatory keywords
    if any(word in phrase_lower for word in ['taste', 'flavor', 'sweet', 'bitter', 'sour', 'salty', 'savory']):
        return 'gustatory'

    # Kinesthetic keywords
    if any(word in phrase_lower for word in ['move', 'motion', 'weight', 'balance', 'dizzy', 'falling', 'rise']):
        return 'kinesthetic'

    # Default to visual
    return 'visual'


def add_phrase(phrase: str, episode: int, sensory_type: str = None):
    """Add a sensory phrase to the vocabulary."""
    vocab = load_vocabulary()
    normalized = normalize_phrase(phrase)

    if not sensory_type:
        sensory_type = classify_sensory_type(phrase)

    if sensory_type not in vocab["vocabulary"]:
        vocab["vocabulary"][sensory_type] = {}

    if normalized in vocab["vocabulary"][sensory_type]:
        # Update existing entry
        entry = vocab["vocabulary"][sensory_type][normalized]
        entry["last_use"] = episode
        entry["count"] = entry.get("count", 1) + 1
        entry["episodes"].append(episode)
        entry["episodes"] = sorted(list(set(entry["episodes"])))
        print(f"[UPDATE] '{phrase}' now used in {entry['count']} episodes", file=sys.stderr)
    else:
        # New entry
        vocab["vocabulary"][sensory_type][normalized] = {
            "original": phrase,
            "first_use": episode,
            "last_use": episode,
            "count": 1,
            "episodes": [episode]
        }
        print(f"[NEW] Added '{phrase}' as {sensory_type} (Episode {episode})", file=sys.stderr)

    save_vocabulary(vocab)


def check_phrase(phrase: str, current_episode: int = None) -> dict:
    """
    Check if a phrase is used and whether it's available for reuse.

    Returns dict with status info.
    """
    vocab = load_vocabulary()
    normalized = normalize_phrase(phrase)
    decay = vocab.get("decay_episodes", DECAY_EPISODES)

    for sensory_type, phrases in vocab["vocabulary"].items():
        if normalized in phrases:
            entry = phrases[normalized]
            last_use = entry.get("last_use", entry.get("first_use", 0))

            result = {
                "found": True,
                "phrase": entry.get("original", phrase),
                "sensory_type": sensory_type,
                "first_use": entry.get("first_use"),
                "last_use": last_use,
                "count": entry.get("count", 1),
                "episodes": entry.get("episodes", []),
            }

            if current_episode:
                episodes_since = current_episode - last_use
                result["episodes_since_use"] = episodes_since
                result["eligible_for_reuse"] = episodes_since >= decay

            return result

    return {"found": False, "phrase": phrase}


def sync_from_episode(episode_num: int):
    """
    Sync sensory vocabulary from episode extractions.

    Reads all used_sensory_language items from the episode.
    """
    ep_dir = EPISODES_DIR / f"{episode_num:03d}"
    if not ep_dir.exists():
        print(f"[ERROR] Episode {episode_num} not found", file=sys.stderr)
        return

    added = 0
    for chunk_file in sorted(ep_dir.glob("chunk-*.json")):
        if "-raw" in chunk_file.name or "-needs-review" in chunk_file.name:
            continue

        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)

            for ext in chunk_data.get("extractions", []):
                if ext.get("content_type") == "used_sensory_language":
                    text = ext.get("text", "")
                    sensory_type = ext.get("sensory_type")
                    if text:
                        add_phrase(text, episode_num, sensory_type)
                        added += 1
        except Exception as e:
            print(f"[WARN] Failed to process {chunk_file.name}: {e}", file=sys.stderr)

    print(f"[DONE] Synced {added} sensory phrases from Episode {episode_num}", file=sys.stderr)


def sync_from_qdrant():
    """Sync sensory vocabulary from Qdrant collection."""
    try:
        # Scroll through all used_sensory_language items
        offset = None
        synced = 0

        while True:
            payload = {
                "filter": {
                    "must": [
                        {"key": "content_type", "match": {"value": "used_sensory_language"}},
                        {"key": "scope", "match": {"value": "series"}}
                    ]
                },
                "limit": 100,
                "with_payload": True,
                "with_vector": False
            }
            if offset:
                payload["offset"] = offset

            response = requests.post(
                f"{QDRANT_URL}/collections/{COLLECTION}/points/scroll",
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                print(f"[ERROR] Qdrant query failed: {response.text}", file=sys.stderr)
                break

            result = response.json().get("result", {})
            points = result.get("points", [])

            for point in points:
                payload = point.get("payload", {})
                text = payload.get("text", "")
                episode = payload.get("episode_number", 0)
                sensory_type = payload.get("sensory_type")
                if text and episode:
                    add_phrase(text, episode, sensory_type)
                    synced += 1

            offset = result.get("next_page_offset")
            if not offset or not points:
                break

        print(f"[DONE] Synced {synced} sensory phrases from Qdrant", file=sys.stderr)

    except Exception as e:
        print(f"[ERROR] Failed to sync from Qdrant: {e}", file=sys.stderr)


def show_status():
    """Display vocabulary statistics."""
    vocab = load_vocabulary()

    print("\n=== SENSORY VOCABULARY STATUS ===\n")
    print(f"Version: {vocab.get('version', '?')}")
    print(f"Decay Episodes: {vocab.get('decay_episodes', DECAY_EPISODES)}")
    print(f"Last Updated: {vocab.get('last_updated', 'Never')}")

    total = 0
    print("\nBy Sensory Type:")
    for sensory_type, phrases in vocab.get("vocabulary", {}).items():
        count = len(phrases)
        total += count
        print(f"  {sensory_type}: {count}")

    print(f"\nTotal Phrases Tracked: {total}")

    # Show most used phrases
    all_phrases = []
    for sensory_type, phrases in vocab.get("vocabulary", {}).items():
        for normalized, entry in phrases.items():
            all_phrases.append({
                "phrase": entry.get("original", normalized),
                "type": sensory_type,
                "count": entry.get("count", 1),
                "last_use": entry.get("last_use", 0)
            })

    if all_phrases:
        print("\nMost Used (Top 10):")
        for item in sorted(all_phrases, key=lambda x: -x["count"])[:10]:
            print(f"  [{item['count']}x] {item['phrase'][:50]}... ({item['type']})")

    print()


def show_available(current_episode: int):
    """Show phrases eligible for reuse at the given episode."""
    vocab = load_vocabulary()
    decay = vocab.get("decay_episodes", DECAY_EPISODES)

    available = []
    for sensory_type, phrases in vocab.get("vocabulary", {}).items():
        for normalized, entry in phrases.items():
            last_use = entry.get("last_use", entry.get("first_use", 0))
            episodes_since = current_episode - last_use

            if episodes_since >= decay:
                available.append({
                    "phrase": entry.get("original", normalized),
                    "type": sensory_type,
                    "last_use": last_use,
                    "episodes_since": episodes_since
                })

    print(f"\n=== PHRASES AVAILABLE FOR REUSE (Episode {current_episode}) ===\n")
    print(f"Decay threshold: {decay} episodes\n")

    if not available:
        print("No phrases are currently eligible for reuse.")
    else:
        print(f"Found {len(available)} phrases eligible for reuse:\n")
        for item in sorted(available, key=lambda x: x["episodes_since"], reverse=True)[:20]:
            print(f"  [{item['episodes_since']} eps ago] {item['phrase'][:60]}... ({item['type']})")

    print()


def main():
    parser = argparse.ArgumentParser(description="Manage sensory vocabulary tracking")
    parser.add_argument("--check", metavar="PHRASE", help="Check if a phrase is used")
    parser.add_argument("--add", metavar="PHRASE", help="Add a new phrase")
    parser.add_argument("--episode", "-e", type=int, help="Episode number for add/check/sync")
    parser.add_argument("--type", "-t", help="Sensory type (visual, auditory, tactile, olfactory, gustatory, kinesthetic)")
    parser.add_argument("--sync", action="store_true", help="Sync from episode extractions (requires --episode)")
    parser.add_argument("--sync-qdrant", action="store_true", help="Sync from Qdrant collection")
    parser.add_argument("--status", action="store_true", help="Show vocabulary statistics")
    parser.add_argument("--available", action="store_true", help="Show phrases available for reuse (requires --episode)")

    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.check:
        result = check_phrase(args.check, args.episode)
        if result["found"]:
            print(f"\n[FOUND] '{result['phrase']}'")
            print(f"  Type: {result['sensory_type']}")
            print(f"  First used: Episode {result['first_use']}")
            print(f"  Last used: Episode {result['last_use']}")
            print(f"  Total uses: {result['count']}")
            if "eligible_for_reuse" in result:
                if result["eligible_for_reuse"]:
                    print(f"  Status: ELIGIBLE for reuse ({result['episodes_since_use']} episodes since last use)")
                else:
                    print(f"  Status: NOT eligible ({result['episodes_since_use']} episodes since last use, need {DECAY_EPISODES})")
        else:
            print(f"\n[NOT FOUND] '{args.check}' is not in the vocabulary - safe to use!")
        print()
    elif args.add:
        if not args.episode:
            print("[ERROR] --episode required when adding a phrase", file=sys.stderr)
            return
        add_phrase(args.add, args.episode, args.type)
    elif args.sync:
        if not args.episode:
            print("[ERROR] --episode required for sync", file=sys.stderr)
            return
        sync_from_episode(args.episode)
    elif args.sync_qdrant:
        sync_from_qdrant()
    elif args.available:
        if not args.episode:
            print("[ERROR] --episode required to check availability", file=sys.stderr)
            return
        show_available(args.episode)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
