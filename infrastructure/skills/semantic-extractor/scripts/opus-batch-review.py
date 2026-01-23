#!/usr/bin/env python3
"""
opus-batch-review.py - Batch review disputed items with Claude Opus

Queries Qdrant for items with 0.85 confidence (2/3 Gemini agreement),
batches them for efficient Opus review, and updates with 0.95 confidence.

Usage:
    # Extract disputed items and create review batches
    python opus-batch-review.py --extract --collection tesla_mandela_effects

    # Apply Opus decisions from a reviewed batch
    python opus-batch-review.py --apply --batch-file batch_001_reviewed.json

    # Check current status
    python opus-batch-review.py --status --collection tesla_mandela_effects

The review process:
1. --extract creates batch files in ./opus-review-batches/
2. Each batch is reviewed by Opus (via Claude Code Task tool)
3. --apply updates Qdrant with the Opus decisions
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from collections import defaultdict

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
except ImportError:
    print("[ERROR] qdrant-client not installed. Run: pip install qdrant-client", file=sys.stderr)
    sys.exit(1)

QDRANT_URL = "http://localhost:6333"
BATCH_SIZE = 50  # Items per batch - fits comfortably in Opus context
OUTPUT_DIR = Path(__file__).parent / "opus-review-batches"

# Content types that should NOT be reviewed (structural, not semantic)
SKIP_TYPES = {'episode_parent', 'episode_chunk', 'episode_full_text', 'series_summary', 'episode_summary'}


def get_disputed_items(collection: str) -> list:
    """Get all items with 0.85 confidence (2/3 agreement, no Opus review)."""
    client = QdrantClient(QDRANT_URL)

    results = client.scroll(
        collection_name=collection,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )

    disputed = []
    for point in results[0]:
        payload = point.payload
        content_type = payload.get('content_type', '')
        confidence = payload.get('confidence', 1.0)
        agreement = payload.get('agreement', '')

        # Skip structural types
        if content_type in SKIP_TYPES:
            continue

        # Skip already Opus-reviewed
        if 'opus' in str(agreement).lower():
            continue

        # Get 0.85 confidence items (2/3 agreement)
        if confidence == 0.85:
            disputed.append({
                'id': str(point.id),
                'content_type': content_type,
                'text': payload.get('text', ''),
                'title': payload.get('title', ''),
                'votes_for': payload.get('votes_for', {}),
                'agreement': agreement,
                'episode_number': payload.get('episode_number'),
                'keywords': payload.get('keywords', [])
            })

    return disputed


def create_batches(items: list, batch_size: int = BATCH_SIZE) -> list:
    """Split items into batches for review."""
    batches = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batches.append(batch)
    return batches


def create_review_prompt(batch: list, batch_num: int) -> str:
    """Create the Opus review prompt for a batch."""
    prompt = f"""# Semantic Extraction Review - Batch {batch_num}

You are reviewing semantic extractions from Tesla Mandela Effects episodes.
Each item below was classified by 2 out of 3 Gemini passes, but 1 disagreed.

Your job: Confirm or correct the classification.

## Valid Content Types

| Type | Description |
|------|-------------|
| historical_fact | Real documented history that cannot change |
| lore_fact | Series-invented canon that is now locked |
| character_state | What a character knows/believes at this point |
| relationship | How entities connect |
| revelation | Major reveal that changes understanding |
| open_mystery | Question deliberately NOT answered |
| proposed_question | Question that MAY be answered later |
| forbidden_conclusion | Must stay ambiguous forever |
| used_imagery | Metaphors/imagery used (tracks recycling) |
| used_sensory_language | Sensory phrases (cannot repeat for 50 episodes) |

## Items to Review

"""

    for i, item in enumerate(batch, 1):
        votes = item.get('votes_for', {})
        if isinstance(votes, dict):
            vote_str = ', '.join(f"{k}: {v}" for k, v in votes.items()) if votes else 'N/A'
        else:
            vote_str = str(votes) if votes else 'N/A'

        prompt += f"""### Item {i}
**Current classification:** {item['content_type']}
**Votes:** {vote_str}
**Text:** {item['text'][:500]}{'...' if len(item['text']) > 500 else ''}

**Your decision:** [CONFIRM or specify correct type]
**Reasoning:** [Brief explanation]

---

"""

    prompt += """## Output Format

Return a JSON array with your decisions:

```json
[
  {"item": 1, "decision": "CONFIRM", "reasoning": "Correctly classified as historical_fact"},
  {"item": 2, "decision": "lore_fact", "reasoning": "This is series-invented, not real history"},
  ...
]
```

Review each item carefully. The accuracy of the lore database depends on this.
"""

    return prompt


def extract_batches(collection: str) -> None:
    """Extract disputed items and create batch files for review."""
    print(f"[INFO] Querying {collection} for disputed items...")

    disputed = get_disputed_items(collection)
    print(f"[INFO] Found {len(disputed)} items with 0.85 confidence")

    if not disputed:
        print("[OK] No disputed items to review!")
        return

    batches = create_batches(disputed)
    print(f"[INFO] Creating {len(batches)} batches of ~{BATCH_SIZE} items each")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for i, batch in enumerate(batches, 1):
        batch_file = OUTPUT_DIR / f"batch_{i:03d}.json"
        prompt_file = OUTPUT_DIR / f"batch_{i:03d}_prompt.md"

        # Save batch data
        batch_data = {
            'batch_number': i,
            'total_batches': len(batches),
            'item_count': len(batch),
            'created': datetime.now().isoformat(),
            'collection': collection,
            'items': batch
        }

        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2)

        # Save review prompt
        prompt = create_review_prompt(batch, i)
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        print(f"[OK] Created {batch_file.name} ({len(batch)} items)")

    print(f"\n[DONE] Created {len(batches)} batch files in {OUTPUT_DIR}")
    print("\nNext steps:")
    print("1. Review each batch_NNN_prompt.md with Claude Opus")
    print("2. Save Opus responses to batch_NNN_reviewed.json")
    print("3. Run: python opus-batch-review.py --apply --batch-file batch_NNN_reviewed.json")


def apply_review(batch_file: Path, collection: str) -> None:
    """Apply Opus review decisions to Qdrant."""
    print(f"[INFO] Loading review file: {batch_file}")

    with open(batch_file, 'r', encoding='utf-8') as f:
        review_data = json.load(f)

    items = review_data.get('items', [])
    decisions = review_data.get('decisions', [])

    if not decisions:
        print("[ERROR] No decisions found in review file. Add 'decisions' array.", file=sys.stderr)
        sys.exit(1)

    client = QdrantClient(QDRANT_URL)

    updated = 0
    changed = 0

    for decision in decisions:
        item_num = decision.get('item', 0) - 1  # Convert to 0-indexed
        if item_num < 0 or item_num >= len(items):
            print(f"[WARN] Invalid item number: {decision.get('item')}", file=sys.stderr)
            continue

        item = items[item_num]
        point_id = item['id']

        new_type = decision.get('decision', 'CONFIRM')
        reasoning = decision.get('reasoning', '')

        # Determine final classification
        if new_type.upper() == 'CONFIRM':
            final_type = item['content_type']
        else:
            final_type = new_type
            changed += 1

        # Update Qdrant
        try:
            # Get current point to preserve other fields
            points = client.retrieve(collection, [point_id], with_payload=True)
            if not points:
                print(f"[WARN] Point not found: {point_id}", file=sys.stderr)
                continue

            current_payload = points[0].payload

            # Update fields
            current_payload['content_type'] = final_type
            current_payload['confidence'] = 0.95
            current_payload['agreement'] = 'opus'
            current_payload['opus_reasoning'] = reasoning
            current_payload['opus_reviewed'] = datetime.now().isoformat()

            # Upsert with updated payload
            client.set_payload(
                collection_name=collection,
                payload=current_payload,
                points=[point_id]
            )

            updated += 1
            status = "CHANGED" if new_type.upper() != 'CONFIRM' else "CONFIRMED"
            print(f"[OK] {status}: {item['text'][:40]}...")

        except Exception as e:
            print(f"[ERROR] Failed to update {point_id}: {e}", file=sys.stderr)

    print(f"\n[DONE] Updated {updated} items ({changed} changed, {updated - changed} confirmed)")


def show_status(collection: str) -> None:
    """Show current review status."""
    client = QdrantClient(QDRANT_URL)

    results = client.scroll(
        collection_name=collection,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )

    stats = defaultdict(int)
    by_confidence = defaultdict(int)

    for point in results[0]:
        payload = point.payload
        content_type = payload.get('content_type', 'unknown')
        confidence = payload.get('confidence', 0)
        agreement = payload.get('agreement', '')

        if content_type in SKIP_TYPES:
            stats['structural'] += 1
        elif 'opus' in str(agreement).lower():
            stats['opus_reviewed'] += 1
            by_confidence['0.95 (opus)'] += 1
        elif confidence == 0.95:
            stats['unanimous'] += 1
            by_confidence['0.95 (unanimous)'] += 1
        elif confidence == 0.85:
            stats['needs_review'] += 1
            by_confidence['0.85 (2/3)'] += 1
        else:
            stats['other'] += 1
            by_confidence[f'{confidence}'] += 1

    print(f"Review Status for {collection}")
    print("=" * 40)
    print(f"Needs Opus review:  {stats['needs_review']}")
    print(f"Opus reviewed:      {stats['opus_reviewed']}")
    print(f"Unanimous (3/3):    {stats['unanimous']}")
    print(f"Structural:         {stats['structural']}")
    print(f"Other:              {stats['other']}")
    print()
    print("By confidence:")
    for conf, count in sorted(by_confidence.items()):
        print(f"  {conf}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Batch review disputed items with Claude Opus")
    parser.add_argument("--extract", action="store_true", help="Extract disputed items and create batch files")
    parser.add_argument("--apply", action="store_true", help="Apply Opus review decisions")
    parser.add_argument("--status", action="store_true", help="Show current review status")
    parser.add_argument("--collection", "-c", default="tesla_mandela_effects", help="Qdrant collection name")
    parser.add_argument("--batch-file", "-b", type=Path, help="Reviewed batch file to apply")

    args = parser.parse_args()

    if args.extract:
        extract_batches(args.collection)
    elif args.apply:
        if not args.batch_file:
            print("[ERROR] --batch-file required with --apply", file=sys.stderr)
            sys.exit(1)
        apply_review(args.batch_file, args.collection)
    elif args.status:
        show_status(args.collection)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
