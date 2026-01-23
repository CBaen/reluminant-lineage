#!/usr/bin/env python3
"""
episode-pipeline.py - Complete episode processing orchestrator

Runs the full pipeline for a completed episode:
1. Chunk episode text
2. Extract semantic data (3-pass voting)
3. Store to Qdrant (with deduplication)
4. Generate episode summary
5. Update series summary
6. Check continuity

Usage:
    python episode-pipeline.py --episode 3 --title "Episode Title" --file "path/to/episode.txt"
    python episode-pipeline.py --episode 3 --title "Episode Title" --file "path/to/episode.txt" --dry-run
    python episode-pipeline.py --episode 3 --skip-extraction  # Just summaries and continuity
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Script locations
SCRIPTS_DIR = Path(__file__).parent
WARDENCLYFFE_DIR = Path.home() / "projects" / "WARDENCLYFFE"

def run_command(cmd: list, description: str, dry_run: bool = False) -> tuple[bool, str]:
    """Run a command and return (success, output)."""
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}[STEP] {description}", file=sys.stderr)
    print(f"  Command: {' '.join(cmd[:3])}...", file=sys.stderr)

    if dry_run:
        return True, "Dry run - skipped"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for extraction
            cwd=str(WARDENCLYFFE_DIR)
        )

        if result.returncode == 0:
            print(f"  [OK] {description} completed", file=sys.stderr)
            return True, result.stdout
        else:
            print(f"  [ERROR] {description} failed: {result.stderr[:200]}", file=sys.stderr)
            return False, result.stderr

    except subprocess.TimeoutExpired:
        print(f"  [ERROR] {description} timed out", file=sys.stderr)
        return False, "Timeout"
    except Exception as e:
        print(f"  [ERROR] {description} exception: {e}", file=sys.stderr)
        return False, str(e)

def step_chunk_episode(episode_file: str, episode_number: int, episode_title: str, dry_run: bool) -> bool:
    """Step 1: Chunk episode and store parent/chunks."""
    extract_script = WARDENCLYFFE_DIR / "extract_episode.py"

    if not extract_script.exists():
        print(f"  [WARN] extract_episode.py not found at {extract_script}", file=sys.stderr)
        return False

    cmd = [
        "python", str(extract_script),
        episode_file,
        str(episode_number),
        episode_title
    ]

    success, _ = run_command(cmd, f"Chunk Episode {episode_number}", dry_run)
    return success

def step_semantic_extraction(episode_number: int, dry_run: bool) -> bool:
    """Step 2: Run 3-pass semantic extraction."""
    migrate_script = SCRIPTS_DIR / "migrate-episodes.py"

    cmd = [
        "python", str(migrate_script),
        "--episode", str(episode_number)
    ]

    success, _ = run_command(cmd, f"Semantic Extraction for Episode {episode_number}", dry_run)
    return success

def step_generate_summary(episode_number: int, dry_run: bool) -> bool:
    """Step 3: Generate episode summary."""
    summary_script = SCRIPTS_DIR / "generate-episode-summary.py"

    cmd = [
        "python", str(summary_script),
        "--episode", str(episode_number)
    ]

    success, _ = run_command(cmd, f"Generate Summary for Episode {episode_number}", dry_run)
    return success

def step_update_series(episode_number: int, dry_run: bool) -> bool:
    """Step 4: Update series summary."""
    series_script = SCRIPTS_DIR / "update-series-summary.py"

    cmd = [
        "python", str(series_script),
        "--episode", str(episode_number)
    ]

    success, _ = run_command(cmd, f"Update Series Summary through Episode {episode_number}", dry_run)
    return success

def step_check_continuity(episode_number: int, dry_run: bool) -> bool:
    """Step 5: Check continuity."""
    continuity_script = SCRIPTS_DIR / "check-continuity.py"

    output_file = SCRIPTS_DIR.parent / "extractions" / "continuity" / f"episode_{episode_number:03d}_continuity.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python", str(continuity_script),
        "--episode", str(episode_number),
        "--output", str(output_file)
    ]

    success, _ = run_command(cmd, f"Check Continuity for Episode {episode_number}", dry_run)
    return success

def step_sync_sensory(episode_number: int, dry_run: bool) -> bool:
    """Step 6: Sync sensory vocabulary."""
    sensory_script = SCRIPTS_DIR / "sensory-vocabulary.py"

    cmd = [
        "python", str(sensory_script),
        "--sync",
        "--episode", str(episode_number)
    ]

    success, _ = run_command(cmd, f"Sync Sensory Vocabulary for Episode {episode_number}", dry_run)
    return success

def main():
    parser = argparse.ArgumentParser(
        description="Complete episode processing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full pipeline for new episode
    python episode-pipeline.py --episode 3 --title "The Third Eye" --file "episodes/003.txt"

    # Skip extraction (episode already extracted)
    python episode-pipeline.py --episode 3 --skip-extraction

    # Dry run to see what would happen
    python episode-pipeline.py --episode 3 --title "Test" --file "test.txt" --dry-run
        """
    )

    parser.add_argument("--episode", "-e", type=int, required=True, help="Episode number")
    parser.add_argument("--title", "-t", help="Episode title")
    parser.add_argument("--file", "-f", help="Path to episode text file")
    parser.add_argument("--skip-chunking", action="store_true", help="Skip chunking step")
    parser.add_argument("--skip-extraction", action="store_true", help="Skip semantic extraction")
    parser.add_argument("--skip-continuity", action="store_true", help="Skip continuity check")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without doing it")

    args = parser.parse_args()

    # Validation
    if not args.skip_chunking and not args.file:
        parser.error("--file is required unless --skip-chunking is specified")

    if not args.skip_chunking and not args.title:
        parser.error("--title is required unless --skip-chunking is specified")

    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"EPISODE COMPLETION PIPELINE - Episode {args.episode}", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)
    print(f"Started: {datetime.now().isoformat()}", file=sys.stderr)

    if args.dry_run:
        print("[DRY-RUN MODE - No changes will be made]", file=sys.stderr)

    results = {}

    # Step 1: Chunk episode
    if not args.skip_chunking:
        results["chunking"] = step_chunk_episode(args.file, args.episode, args.title, args.dry_run)
        if not results["chunking"] and not args.dry_run:
            print("\n[ABORT] Chunking failed - stopping pipeline", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n[SKIP] Chunking (--skip-chunking)", file=sys.stderr)
        results["chunking"] = "skipped"

    # Step 2: Semantic extraction
    if not args.skip_extraction:
        results["extraction"] = step_semantic_extraction(args.episode, args.dry_run)
        if not results["extraction"] and not args.dry_run:
            print("\n[ABORT] Extraction failed - stopping pipeline", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n[SKIP] Semantic Extraction (--skip-extraction)", file=sys.stderr)
        results["extraction"] = "skipped"

    # Step 3: Generate episode summary
    results["episode_summary"] = step_generate_summary(args.episode, args.dry_run)

    # Step 4: Update series summary
    results["series_summary"] = step_update_series(args.episode, args.dry_run)

    # Step 5: Check continuity
    if not args.skip_continuity and args.episode > 1:
        results["continuity"] = step_check_continuity(args.episode, args.dry_run)
    else:
        if args.episode == 1:
            print("\n[SKIP] Continuity check (Episode 1 has nothing to compare)", file=sys.stderr)
        else:
            print("\n[SKIP] Continuity check (--skip-continuity)", file=sys.stderr)
        results["continuity"] = "skipped"

    # Step 6: Sync sensory vocabulary
    results["sensory"] = step_sync_sensory(args.episode, args.dry_run)

    # Final report
    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"PIPELINE COMPLETE - Episode {args.episode}", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)
    print(f"Finished: {datetime.now().isoformat()}", file=sys.stderr)
    print(f"\nResults:", file=sys.stderr)

    for step, result in results.items():
        status = "[OK]" if result == True else "[SKIP]" if result == "skipped" else "[FAIL]"
        print(f"  {status} {step}", file=sys.stderr)

    failures = [k for k, v in results.items() if v == False]
    if failures:
        print(f"\n[WARN] Some steps failed: {', '.join(failures)}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\n[SUCCESS] Episode {args.episode} fully processed!", file=sys.stderr)

if __name__ == "__main__":
    main()
