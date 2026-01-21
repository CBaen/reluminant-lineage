#!/usr/bin/env python3
"""
apply-opus-review.py - Apply Opus review decisions and add to extractions

After Claude/Opus reviews the disagreed items, this script applies
those decisions and adds them to the main extraction file.

Usage:
    python apply-opus-review.py --review-file chunk6-needs-review.json --extraction-file chunk6.json

The review file should have your_classification and your_reasoning filled in.
"""

import argparse
import json
import sys
from pathlib import Path


def apply_review(review_file: Path, extraction_file: Path) -> bool:
    """Apply Opus review decisions to extraction file."""

    # Load review file
    try:
        with open(review_file, 'r', encoding='utf-8') as f:
            review_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read review file: {e}", file=sys.stderr)
        return False

    # Load extraction file
    try:
        with open(extraction_file, 'r', encoding='utf-8') as f:
            extraction_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read extraction file: {e}", file=sys.stderr)
        return False

    episode = extraction_data.get("episode")
    chunk_index = extraction_data.get("chunk_index")

    # Process reviewed items
    added = 0
    skipped = 0

    for item in review_data.get("items", []):
        classification = item.get("your_classification")
        reasoning = item.get("your_reasoning")

        if not classification:
            print(f"[SKIP] No classification for: {item.get('text', '')[:40]}...", file=sys.stderr)
            skipped += 1
            continue

        # Create extraction entry
        new_extraction = {
            "content_type": classification,
            "text": item.get("text"),
            "reasoning": reasoning or item.get("gemini_reasoning"),
            "confidence": 0.90,  # Opus-reviewed confidence
            "agreement": "opus",  # Marked as Opus-reviewed
            "episode_number": episode,
            "chunk_index": chunk_index
        }

        extraction_data["extractions"].append(new_extraction)
        added += 1
        print(f"[OK] Added [{classification}]: {item.get('text', '')[:40]}...", file=sys.stderr)

    # Update extraction file
    extraction_data["opus_reviewed"] = True
    extraction_data["opus_added"] = added

    with open(extraction_file, 'w', encoding='utf-8') as f:
        json.dump(extraction_data, f, indent=2)

    print(f"[DONE] Added {added} items, skipped {skipped}", file=sys.stderr)
    return True


def main():
    parser = argparse.ArgumentParser(description="Apply Opus review decisions")
    parser.add_argument("--review-file", "-r", required=True, help="Review JSON file with Opus decisions")
    parser.add_argument("--extraction-file", "-e", required=True, help="Extraction JSON file to update")

    args = parser.parse_args()

    review_path = Path(args.review_file)
    extraction_path = Path(args.extraction_file)

    if not review_path.exists():
        print(f"[ERROR] Review file not found: {review_path}", file=sys.stderr)
        sys.exit(1)

    if not extraction_path.exists():
        print(f"[ERROR] Extraction file not found: {extraction_path}", file=sys.stderr)
        sys.exit(1)

    success = apply_review(review_path, extraction_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
