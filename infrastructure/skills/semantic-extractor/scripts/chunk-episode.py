#!/usr/bin/env python3
"""
chunk-episode.py - Split episode scripts into properly-sized chunks

FINALIZED PARAMETERS (January 2026 Research):
- Target: 650 words (optimal for narrative content)
- Min: 400 words (ensures minimum context)
- Max: 800 words (V3 schema limit)
- Overlap: 97 words (~15% - critical for narrative continuity)
- Strategy: Scene-aware paragraph-based with overlap

Usage:
    python chunk-episode.py --source <script.txt> --episode <num>
    python chunk-episode.py --source <script.txt> --episode <num> --dry-run
"""

import argparse
import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
EPISODES_DIR = SKILL_DIR / "extractions" / "episodes"

# FINALIZED PARAMETERS (from comprehensive research - DO NOT CHANGE)
TARGET_WORDS = 650      # Optimal for narrative content (500-1024 range)
MIN_WORDS = 400         # Ensures minimum context
MAX_WORDS = 800         # V3 schema limit (was incorrectly 850/900)
OVERLAP_WORDS = 97      # ~15% overlap for narrative continuity (was 65)


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs (double newline separated)."""
    text = text.replace('\r\n', '\n')
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def is_scene_break(paragraph: str) -> bool:
    """
    Detect if paragraph ends at a natural scene break.
    Scene breaks are preferred chunk boundaries for narrative coherence.
    """
    # Ends with strong punctuation
    if paragraph.rstrip().endswith(('.', '?', '!', '"', "'")):
        # Check for scene break indicators
        lower = paragraph.lower()
        indicators = [
            # Time transitions
            'later', 'the next', 'morning', 'evening', 'night', 'dawn', 'dusk',
            # Location transitions
            'outside', 'inside', 'across', 'meanwhile', 'elsewhere',
            # POV/focus shifts
            'turned', 'looked', 'watched', 'saw', 'heard',
            # Emotional beats
            'understood', 'realized', 'knew', 'felt', 'remembered'
        ]
        # If ends with period/etc AND contains scene indicator, it's a good break point
        for indicator in indicators:
            if indicator in lower:
                return True
        # Even without indicators, strong punctuation is acceptable
        return True
    return False


def chunk_paragraphs_with_overlap(paragraphs: list[str]) -> list[tuple[str, str, bool]]:
    """
    Group paragraphs into chunks with overlap.

    Returns list of tuples: (clean_chunk, chunk_with_overlap, has_overlap)
    - clean_chunk: The actual content without overlap (for word counting)
    - chunk_with_overlap: The content prefixed with overlap from previous chunk
    - has_overlap: Boolean (first chunk = False)
    """
    # First pass: create chunks without overlap
    chunks = []
    current_chunk = []
    current_words = 0

    for para in paragraphs:
        para_words = count_words(para)

        # If this paragraph alone exceeds max, it becomes its own chunk
        if para_words > MAX_WORDS:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            chunks.append(para)
            current_chunk = []
            current_words = 0
            continue

        # Would adding this paragraph exceed max?
        if current_words + para_words > MAX_WORDS and current_words >= MIN_WORDS:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_words = para_words
        else:
            current_chunk.append(para)
            current_words += para_words

            # If we've hit target and paragraph is a scene break, finalize
            if current_words >= TARGET_WORDS and is_scene_break(para):
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_words = 0

    # Don't forget the last chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    # Second pass: add overlap
    chunks_with_overlap = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            # First chunk has no overlap
            chunks_with_overlap.append((chunk, chunk, False))
        else:
            # Get overlap from previous chunk (last OVERLAP_WORDS words)
            prev_words = chunks[i-1].split()
            if len(prev_words) > OVERLAP_WORDS:
                overlap_text = ' '.join(prev_words[-OVERLAP_WORDS:])
            else:
                overlap_text = chunks[i-1]

            # Prefix with overlap marker
            chunk_with_overlap = f"[...] {overlap_text}\n\n{chunk}"
            chunks_with_overlap.append((chunk, chunk_with_overlap, True))

    return chunks_with_overlap


def remove_caption_key(text: str) -> str:
    """Remove the CAPTION KEY section from the end of scripts."""
    marker = "CAPTION KEY"
    if marker in text:
        idx = text.find(marker)
        line_start = text.rfind('\n', 0, idx)
        if line_start != -1:
            text = text[:line_start].strip()
    return text


def main():
    parser = argparse.ArgumentParser(
        description="Chunk episode scripts for semantic extraction (V3 parameters)"
    )
    parser.add_argument("--source", "-s", required=True, help="Path to source script file")
    parser.add_argument("--episode", "-e", type=int, required=True, help="Episode number")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--clear-existing", action="store_true", help="Clear existing files first")
    parser.add_argument("--no-overlap", action="store_true", help="Disable overlap (not recommended)")

    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"[ERROR] Source file not found: {source_path}")
        return 1

    # Read source
    with open(source_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Remove BOM if present
    if text.startswith('\ufeff'):
        text = text[1:]

    # Remove CAPTION KEY section
    text = remove_caption_key(text)

    total_words = count_words(text)
    print(f"\n{'='*60}")
    print(f"EPISODE CHUNKING (V3 Parameters)")
    print(f"{'='*60}")
    print(f"\n[SOURCE] {source_path.name}")
    print(f"  Total words: {total_words}")

    # Split into paragraphs
    paragraphs = split_into_paragraphs(text)
    print(f"  Paragraphs: {len(paragraphs)}")

    # Chunk with overlap
    print(f"\n[PARAMETERS]")
    print(f"  Target: {TARGET_WORDS} words")
    print(f"  Min: {MIN_WORDS} words")
    print(f"  Max: {MAX_WORDS} words")
    print(f"  Overlap: {OVERLAP_WORDS} words (~15%)")

    chunks = chunk_paragraphs_with_overlap(paragraphs)

    # Stats (using clean chunks for word counts)
    word_counts = [count_words(c[0]) for c in chunks]
    print(f"\n[RESULT]")
    print(f"  Chunks created: {len(chunks)}")
    print(f"  Word range: {min(word_counts)}-{max(word_counts)}")
    print(f"  Average: {sum(word_counts) // len(word_counts)} words")

    # Output directory
    ep_dir = EPISODES_DIR / f"{args.episode:03d}"

    if args.dry_run:
        print(f"\n[DRY-RUN] Would write to: {ep_dir}")
        for i, (clean, with_overlap, has_overlap) in enumerate(chunks, 1):
            overlap_note = " (+overlap)" if has_overlap else ""
            print(f"  chunk-{i:02d}-raw.txt: {count_words(clean)} words{overlap_note}")
        return 0

    # Create directory
    ep_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing if requested
    if args.clear_existing:
        print(f"\n[CLEAR] Removing existing files...")
        for f in ep_dir.glob("chunk-*"):
            f.unlink()
            print(f"  Removed: {f.name}")

    # Write chunks (with overlap by default)
    print(f"\n[WRITE] Writing to: {ep_dir}")
    for i, (clean, with_overlap, has_overlap) in enumerate(chunks, 1):
        chunk_path = ep_dir / f"chunk-{i:02d}-raw.txt"

        # Write version with overlap unless disabled
        content = clean if args.no_overlap else with_overlap
        with open(chunk_path, 'w', encoding='utf-8') as f:
            f.write(content)

        overlap_note = " (+overlap)" if has_overlap and not args.no_overlap else ""
        print(f"  chunk-{i:02d}-raw.txt: {count_words(clean)} words{overlap_note}")

    print(f"\n[OK] Episode {args.episode} chunked into {len(chunks)} files")
    print(f"     Overlap: {'disabled' if args.no_overlap else 'enabled (97 words)'}")
    return 0


if __name__ == "__main__":
    exit(main())
