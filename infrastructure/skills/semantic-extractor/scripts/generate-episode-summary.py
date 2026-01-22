#!/usr/bin/env python3
"""
generate-episode-summary.py - Auto-generate episode metadata after extraction

V3 Feature: Aggregates extraction data into episode_summary content type.

Usage:
    python generate-episode-summary.py --episode 2           # Generate summary for episode 2
    python generate-episode-summary.py --all                 # Generate summaries for all episodes
    python generate-episode-summary.py --episode 2 --store   # Generate and store to Qdrant
"""

import argparse
import json
import sys
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests

# Configuration
QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
COLLECTION = "tesla_mandela_effects"

# Directories
SKILL_DIR = Path(__file__).parent.parent
EXTRACTIONS_DIR = SKILL_DIR / "extractions"
EPISODES_DIR = EXTRACTIONS_DIR / "episodes"
SUMMARIES_DIR = EXTRACTIONS_DIR / "summaries"


def ensure_directories():
    """Create summary directory if needed."""
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)


def get_episode_dir(episode_num: int) -> Path:
    """Get the directory for an episode."""
    return EPISODES_DIR / f"{episode_num:03d}"


def load_all_extractions(episode_num: int) -> list:
    """Load all extractions for an episode from chunk files."""
    ep_dir = get_episode_dir(episode_num)
    if not ep_dir.exists():
        return []

    all_extractions = []
    for chunk_file in sorted(ep_dir.glob("chunk-*.json")):
        # Skip raw text files and review files
        if "-raw" in chunk_file.name or "-needs-review" in chunk_file.name:
            continue

        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
            all_extractions.extend(chunk_data.get("extractions", []))
        except Exception as e:
            print(f"[WARN] Failed to load {chunk_file.name}: {e}", file=sys.stderr)

    return all_extractions


def generate_summary(episode_num: int) -> dict:
    """
    Generate episode summary from extractions.

    Aggregates:
    - Characters mentioned
    - Relationships established
    - Timeline covered
    - Key revelations
    - Open mysteries introduced
    - Extraction counts by type
    """
    extractions = load_all_extractions(episode_num)

    if not extractions:
        return {"error": f"No extractions found for episode {episode_num}"}

    # Initialize counters
    characters = set()
    relationships = []
    revelations = []
    open_mysteries = []
    proposed_questions = []
    lore_facts = []
    historical_facts = []
    sensory_language = []
    timeline_dates = set()
    type_counts = Counter()

    # Process all extractions
    for ext in extractions:
        content_type = ext.get("content_type", "unknown")
        type_counts[content_type] += 1
        text = ext.get("text", "")

        if content_type == "character_state":
            # Extract character names from text (simple heuristic)
            # Look for capitalized words that might be names
            words = text.split()
            for word in words:
                clean = word.strip(".,;:!?\"'()[]")
                if clean and clean[0].isupper() and len(clean) > 2:
                    # Common Tesla-related names
                    if clean in ["Tesla", "Nikola", "Dane", "Djuka", "Milutin", "Edison", "Morgan", "Westinghouse"]:
                        characters.add(clean)

        elif content_type == "relationship":
            entity_a = ext.get("entity_a", "")
            entity_b = ext.get("entity_b", "")
            rel_type = ext.get("relationship_type", "unknown")
            if entity_a and entity_b:
                relationships.append({
                    "entities": [entity_a, entity_b],
                    "type": rel_type,
                    "text": text[:100]
                })
                characters.add(entity_a)
                characters.add(entity_b)

        elif content_type == "revelation":
            revelations.append(text[:200])

        elif content_type == "open_mystery":
            open_mysteries.append(text[:200])

        elif content_type == "proposed_question":
            proposed_questions.append(text[:200])

        elif content_type == "lore_fact":
            lore_facts.append(text[:200])

        elif content_type == "historical_fact":
            historical_facts.append(text[:200])

        elif content_type == "used_sensory_language":
            sensory_language.append(text[:100])

        # Look for timeline references
        timeline = ext.get("timeline_date") or ext.get("temporal_context")
        if timeline:
            timeline_dates.add(timeline)

    # Build summary
    summary = {
        "content_type": "episode_summary",
        "episode_number": episode_num,
        "generated_at": datetime.now().isoformat(),
        "extraction_version": 3,

        # Counts
        "total_extractions": len(extractions),
        "extraction_counts": dict(type_counts),

        # Characters
        "characters_mentioned": sorted(list(characters)),
        "character_count": len(characters),

        # Relationships
        "relationships_established": relationships[:20],  # Top 20
        "relationship_count": len(relationships),

        # Story elements
        "key_revelations": revelations[:10],  # Top 10
        "revelation_count": len(revelations),

        "open_mysteries_introduced": open_mysteries[:10],
        "mystery_count": len(open_mysteries),

        "proposed_questions": proposed_questions[:10],
        "question_count": len(proposed_questions),

        # Facts
        "lore_fact_count": len(lore_facts),
        "historical_fact_count": len(historical_facts),
        "sample_lore_facts": lore_facts[:5],
        "sample_historical_facts": historical_facts[:5],

        # Style
        "sensory_language_count": len(sensory_language),
        "sample_sensory_language": sensory_language[:10],

        # Timeline
        "timeline_references": sorted(list(timeline_dates)),
    }

    return summary


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
        return None
    except Exception:
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


def store_summary_to_qdrant(summary: dict, session: str) -> str | None:
    """Store episode summary to Qdrant."""
    point_id = str(uuid.uuid4())

    # Create embedding text from key fields
    embed_parts = [
        f"Episode {summary.get('episode_number')} summary",
        f"Characters: {', '.join(summary.get('characters_mentioned', []))}",
        f"Revelations: {len(summary.get('key_revelations', []))}",
        f"Mysteries: {len(summary.get('open_mysteries_introduced', []))}",
    ]
    embed_text = " ".join(embed_parts)

    dense = get_embedding(embed_text)
    if dense is None:
        print("[ERROR] Failed to get embedding for summary", file=sys.stderr)
        return None

    sparse_indices, sparse_values = get_sparse_vector(embed_text)

    # Flatten summary for Qdrant payload (no nested objects > 1 level)
    payload = {
        "content_type": "episode_summary",
        "episode_number": summary.get("episode_number"),
        "title": f"Episode {summary.get('episode_number')} Summary",
        "text": json.dumps(summary, indent=2)[:10000],  # Store full summary as text
        "timestamp": int(datetime.now().timestamp()),
        "session": session,
        "project": "wardenclyffe",
        "extraction_version": 3,

        # Searchable fields
        "total_extractions": summary.get("total_extractions"),
        "character_count": summary.get("character_count"),
        "relationship_count": summary.get("relationship_count"),
        "revelation_count": summary.get("revelation_count"),
        "mystery_count": summary.get("mystery_count"),
        "characters": summary.get("characters_mentioned", []),
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


def save_summary_to_file(summary: dict, episode_num: int):
    """Save summary to local file."""
    ensure_directories()
    summary_file = SUMMARIES_DIR / f"episode_{episode_num:03d}_summary.json"

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"[OK] Summary saved to {summary_file}", file=sys.stderr)
    return summary_file


def display_summary(summary: dict):
    """Display summary in human-readable format."""
    ep = summary.get("episode_number", "?")

    print(f"\n{'='*60}")
    print(f"EPISODE {ep} SUMMARY")
    print(f"{'='*60}\n")

    print(f"Total Extractions: {summary.get('total_extractions', 0)}")
    print(f"\nExtraction Counts:")
    for ctype, count in sorted(summary.get("extraction_counts", {}).items()):
        print(f"  {ctype}: {count}")

    print(f"\nCharacters ({summary.get('character_count', 0)}):")
    for char in summary.get("characters_mentioned", []):
        print(f"  - {char}")

    print(f"\nRelationships ({summary.get('relationship_count', 0)}):")
    for rel in summary.get("relationships_established", [])[:5]:
        print(f"  - {rel['entities'][0]} <-> {rel['entities'][1]} ({rel['type']})")

    if summary.get("key_revelations"):
        print(f"\nKey Revelations ({summary.get('revelation_count', 0)}):")
        for rev in summary.get("key_revelations", [])[:3]:
            print(f"  - {rev[:80]}...")

    if summary.get("open_mysteries_introduced"):
        print(f"\nOpen Mysteries ({summary.get('mystery_count', 0)}):")
        for mys in summary.get("open_mysteries_introduced", [])[:3]:
            print(f"  - {mys[:80]}...")

    if summary.get("timeline_references"):
        print(f"\nTimeline References:")
        for tl in summary.get("timeline_references", [])[:5]:
            print(f"  - {tl}")

    print(f"\nSensory Language: {summary.get('sensory_language_count', 0)} items tracked")
    print(f"Lore Facts: {summary.get('lore_fact_count', 0)}")
    print(f"Historical Facts: {summary.get('historical_fact_count', 0)}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate episode summaries from extractions")
    parser.add_argument("--episode", "-e", type=int, help="Episode number to summarize")
    parser.add_argument("--all", action="store_true", help="Generate summaries for all episodes")
    parser.add_argument("--store", action="store_true", help="Store summary to Qdrant")
    parser.add_argument("--quiet", "-q", action="store_true", help="Don't display summary")

    args = parser.parse_args()

    if not args.episode and not args.all:
        parser.print_help()
        return

    episodes_to_process = []

    if args.all:
        # Find all episode directories
        for ep_dir in EPISODES_DIR.iterdir():
            if ep_dir.is_dir() and ep_dir.name.isdigit():
                episodes_to_process.append(int(ep_dir.name))
        episodes_to_process.sort()
    else:
        episodes_to_process = [args.episode]

    session = f"SummaryGenerator-{datetime.now().strftime('%Y-%m-%d')}"

    for episode_num in episodes_to_process:
        print(f"[INFO] Processing Episode {episode_num}...", file=sys.stderr)

        summary = generate_summary(episode_num)

        if "error" in summary:
            print(f"[ERROR] {summary['error']}", file=sys.stderr)
            continue

        # Save to file
        save_summary_to_file(summary, episode_num)

        # Display
        if not args.quiet:
            display_summary(summary)

        # Store to Qdrant
        if args.store:
            point_id = store_summary_to_qdrant(summary, session)
            if point_id:
                print(f"[OK] Stored to Qdrant: {point_id}", file=sys.stderr)
            else:
                print(f"[ERROR] Failed to store to Qdrant", file=sys.stderr)


if __name__ == "__main__":
    main()
