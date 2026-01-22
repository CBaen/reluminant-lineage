#!/usr/bin/env python3
"""
migrate-episodes.py - Re-process episodes with V3 pipeline

Performs a full migration:
1. Backup and reset Qdrant collection
2. Re-extract each episode with fixed voting algorithm
3. Apply deduplication
4. Store to Qdrant
5. Generate episode summaries
6. Sync sensory vocabulary

Usage:
    python migrate-episodes.py --dry-run                    # Show what would be done
    python migrate-episodes.py --episodes 1,2              # Migrate specific episodes
    python migrate-episodes.py --all                       # Migrate all episodes
    python migrate-episodes.py --all --skip-reset          # Migrate without resetting collection
    python migrate-episodes.py --status                    # Show migration status
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent
EXTRACTIONS_DIR = SKILL_DIR / "extractions"
EPISODES_DIR = EXTRACTIONS_DIR / "episodes"
MIGRATION_LOG = SKILL_DIR / "migration_log.json"

# Scripts
RESET_SCRIPT = SCRIPTS_DIR / "reset-collection.py"
EXTRACT_SCRIPT = SCRIPTS_DIR / "extract-chunk.py"
STORE_SCRIPT = SCRIPTS_DIR / "store-extractions.py"
SUMMARY_SCRIPT = SCRIPTS_DIR / "generate-episode-summary.py"
SENSORY_SCRIPT = SCRIPTS_DIR / "sensory-vocabulary.py"


def load_migration_log() -> dict:
    """Load migration log."""
    if MIGRATION_LOG.exists():
        with open(MIGRATION_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "3.0",
        "migrations": []
    }


def save_migration_log(log: dict):
    """Save migration log."""
    with open(MIGRATION_LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)


def run_script(script_path: Path, args: list, dry_run: bool = False) -> tuple[bool, str]:
    """Run a Python script with arguments."""
    cmd = ["python", str(script_path)] + args

    if dry_run:
        print(f"  [DRY-RUN] Would run: {' '.join(cmd)}", file=sys.stderr)
        return True, "dry-run"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per script
        )

        if result.returncode == 0:
            return True, result.stdout + result.stderr
        else:
            return False, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)


def get_episode_chunks(episode_num: int) -> list:
    """Get list of raw chunk files for an episode."""
    ep_dir = EPISODES_DIR / f"{episode_num:03d}"
    if not ep_dir.exists():
        return []

    chunks = []
    for chunk_file in sorted(ep_dir.glob("chunk-*-raw.txt")):
        chunks.append(chunk_file)

    return chunks


def get_available_episodes() -> list:
    """Get list of episodes with raw chunks available."""
    episodes = []
    for ep_dir in EPISODES_DIR.iterdir():
        if ep_dir.is_dir() and ep_dir.name.isdigit():
            ep_num = int(ep_dir.name)
            chunks = get_episode_chunks(ep_num)
            if chunks:
                episodes.append(ep_num)
    return sorted(episodes)


def clear_episode_extractions(episode_num: int):
    """Clear existing extraction JSON files for an episode (keep raw chunks)."""
    ep_dir = EPISODES_DIR / f"{episode_num:03d}"
    if not ep_dir.exists():
        return

    # Remove chunk JSON files (but keep raw text files)
    for json_file in ep_dir.glob("chunk-*.json"):
        if "-raw" not in json_file.name:
            json_file.unlink()
            print(f"  Removed: {json_file.name}", file=sys.stderr)

    # Remove manifest
    manifest = ep_dir / "manifest.json"
    if manifest.exists():
        manifest.unlink()
        print(f"  Removed: manifest.json", file=sys.stderr)


def purge_v2_data(dry_run: bool = False):
    """
    Full purge of V2 data:
    - Delete all archived JSONs
    - Delete all extraction JSONs (keep raw text)
    - Clear index.json
    - Delete flagged items
    - Delete summaries

    Raw text chunks (-raw.txt) are PRESERVED for re-extraction.
    """
    print("\n[PURGE] Removing all V2 data...", file=sys.stderr)

    deleted = 0

    # 1. Clear archived folder
    archived_dir = EXTRACTIONS_DIR / "archived"
    if archived_dir.exists():
        for f in archived_dir.glob("*.json"):
            if not dry_run:
                f.unlink()
            deleted += 1
        print(f"  Archived: {deleted} files", file=sys.stderr)

    # 2. Clear flagged folder
    flagged_dir = EXTRACTIONS_DIR / "flagged"
    flagged_count = 0
    if flagged_dir.exists():
        for f in flagged_dir.glob("*.json"):
            if not dry_run:
                f.unlink()
            flagged_count += 1
        print(f"  Flagged: {flagged_count} files", file=sys.stderr)
    deleted += flagged_count

    # 3. Clear summaries folder
    summaries_dir = EXTRACTIONS_DIR / "summaries"
    summary_count = 0
    if summaries_dir.exists():
        for f in summaries_dir.glob("*.json"):
            if not dry_run:
                f.unlink()
            summary_count += 1
        print(f"  Summaries: {summary_count} files", file=sys.stderr)
    deleted += summary_count

    # 4. Clear all episode extraction JSONs (keep raw text)
    episode_count = 0
    for ep_dir in EPISODES_DIR.iterdir():
        if ep_dir.is_dir():
            for json_file in ep_dir.glob("*.json"):
                if not dry_run:
                    json_file.unlink()
                episode_count += 1
    print(f"  Episode JSONs: {episode_count} files", file=sys.stderr)
    deleted += episode_count

    # 5. Clear index.json
    index_file = EXTRACTIONS_DIR / "index.json"
    if index_file.exists():
        if not dry_run:
            index_file.unlink()
        deleted += 1
        print(f"  Index: cleared", file=sys.stderr)

    # Count preserved raw chunks
    raw_count = 0
    for ep_dir in EPISODES_DIR.iterdir():
        if ep_dir.is_dir():
            raw_count += len(list(ep_dir.glob("*-raw.txt")))

    print(f"\n[PURGE] Total deleted: {deleted} files", file=sys.stderr)
    print(f"[PURGE] Preserved: {raw_count} raw text chunks for re-extraction", file=sys.stderr)


def migrate_episode(episode_num: int, dry_run: bool = False) -> dict:
    """
    Migrate a single episode through the V3 pipeline.

    Returns migration result dict.
    """
    result = {
        "episode": episode_num,
        "started_at": datetime.now().isoformat(),
        "steps": {},
        "success": False
    }

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"MIGRATING EPISODE {episode_num}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    # Step 1: Get raw chunks
    chunks = get_episode_chunks(episode_num)
    if not chunks:
        result["error"] = "No raw chunk files found"
        print(f"[ERROR] No raw chunks for Episode {episode_num}", file=sys.stderr)
        return result

    print(f"\n[1/5] Found {len(chunks)} raw chunks", file=sys.stderr)
    result["steps"]["chunks_found"] = len(chunks)

    # Step 2: Clear old extractions
    print(f"\n[2/5] Clearing old extractions...", file=sys.stderr)
    if not dry_run:
        clear_episode_extractions(episode_num)
    result["steps"]["cleared"] = True

    # Step 3: Re-extract each chunk
    print(f"\n[3/5] Extracting with V3 pipeline...", file=sys.stderr)
    extracted = 0
    failed = 0

    for i, chunk_file in enumerate(chunks, 1):
        # Parse chunk index from filename (e.g., chunk-05-raw.txt -> 5)
        chunk_name = chunk_file.stem  # chunk-05-raw
        parts = chunk_name.split("-")
        if len(parts) >= 2:
            chunk_index = int(parts[1])
        else:
            chunk_index = i

        output_file = chunk_file.parent / f"chunk-{chunk_index:02d}.json"

        print(f"  Extracting chunk {chunk_index}...", file=sys.stderr)

        success, output = run_script(
            EXTRACT_SCRIPT,
            [
                "--chunk-file", str(chunk_file),
                "--episode", str(episode_num),
                "--chunk-index", str(chunk_index),
                "--output", str(output_file)
            ],
            dry_run=dry_run
        )

        if success:
            extracted += 1
        else:
            failed += 1
            print(f"    [WARN] Failed: {output[:100]}", file=sys.stderr)

    result["steps"]["extracted"] = extracted
    result["steps"]["extract_failed"] = failed
    print(f"  Extracted: {extracted}, Failed: {failed}", file=sys.stderr)

    if failed > 0 and not dry_run:
        print(f"[WARN] {failed} chunks failed extraction", file=sys.stderr)

    # Step 4: Store to Qdrant with deduplication
    print(f"\n[4/5] Storing to Qdrant with deduplication...", file=sys.stderr)

    # First, save extractions to hub
    ep_dir = EPISODES_DIR / f"{episode_num:03d}"
    for json_file in sorted(ep_dir.glob("chunk-*.json")):
        if "-needs-review" not in json_file.name and "-raw" not in json_file.name:
            success, output = run_script(
                STORE_SCRIPT,
                ["--save-extraction", str(json_file)],
                dry_run=dry_run
            )

    # Then store to Qdrant
    success, output = run_script(
        STORE_SCRIPT,
        ["--store-episode", str(episode_num)],
        dry_run=dry_run
    )
    result["steps"]["stored"] = success
    if not success:
        print(f"  [WARN] Storage issues: {output[:200]}", file=sys.stderr)

    # Step 5: Generate summary
    print(f"\n[5/5] Generating episode summary...", file=sys.stderr)
    success, output = run_script(
        SUMMARY_SCRIPT,
        ["--episode", str(episode_num), "--store", "--quiet"],
        dry_run=dry_run
    )
    result["steps"]["summary"] = success

    # Sync sensory vocabulary
    print(f"\n[BONUS] Syncing sensory vocabulary...", file=sys.stderr)
    success, output = run_script(
        SENSORY_SCRIPT,
        ["--sync", "--episode", str(episode_num)],
        dry_run=dry_run
    )
    result["steps"]["sensory_sync"] = success

    result["completed_at"] = datetime.now().isoformat()
    result["success"] = (failed == 0)

    print(f"\n[{'OK' if result['success'] else 'PARTIAL'}] Episode {episode_num} migration complete", file=sys.stderr)

    return result


def reset_collection(dry_run: bool = False) -> bool:
    """Reset Qdrant collection with V3 schema."""
    print("\n[RESET] Resetting Qdrant collection...", file=sys.stderr)

    success, output = run_script(
        RESET_SCRIPT,
        ["--reset"],
        dry_run=dry_run
    )

    if success:
        print("[OK] Collection reset complete", file=sys.stderr)
    else:
        print(f"[ERROR] Reset failed: {output[:200]}", file=sys.stderr)

    return success


def show_status():
    """Show migration status."""
    print("\n=== MIGRATION STATUS ===\n")

    # Available episodes
    episodes = get_available_episodes()
    print(f"Episodes with raw chunks: {episodes}")

    # Chunk counts
    for ep in episodes:
        chunks = get_episode_chunks(ep)
        print(f"  Episode {ep}: {len(chunks)} chunks")

    # Migration log
    log = load_migration_log()
    if log.get("migrations"):
        print(f"\nPrevious Migrations:")
        for migration in log["migrations"][-5:]:  # Last 5
            print(f"  {migration.get('started_at', '?')}: Episodes {migration.get('episodes', '?')}")
            print(f"    Success: {migration.get('overall_success', '?')}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Migrate episodes to V3 pipeline")
    parser.add_argument("--episodes", "-e", help="Comma-separated episode numbers (e.g., 1,2)")
    parser.add_argument("--all", action="store_true", help="Migrate all available episodes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    parser.add_argument("--skip-reset", action="store_true", help="Skip collection reset")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--purge-v2", action="store_true", help="Full purge of V2 data before migration (keeps raw text)")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if not args.episodes and not args.all:
        parser.print_help()
        return

    # Determine episodes to migrate
    if args.all:
        episodes = get_available_episodes()
    else:
        episodes = [int(e.strip()) for e in args.episodes.split(",")]

    if not episodes:
        print("[ERROR] No episodes to migrate", file=sys.stderr)
        return

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"V3 MIGRATION - Episodes: {episodes}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    if args.dry_run:
        print("\n[DRY-RUN MODE] No changes will be made\n", file=sys.stderr)

    # Purge V2 data if requested
    if args.purge_v2:
        purge_v2_data(dry_run=args.dry_run)

    # Reset collection (unless skipped)
    if not args.skip_reset:
        if not reset_collection(dry_run=args.dry_run):
            if not args.dry_run:
                print("[ERROR] Collection reset failed, aborting", file=sys.stderr)
                return

    # Migrate each episode
    migration_record = {
        "started_at": datetime.now().isoformat(),
        "episodes": episodes,
        "dry_run": args.dry_run,
        "results": []
    }

    for episode_num in episodes:
        result = migrate_episode(episode_num, dry_run=args.dry_run)
        migration_record["results"].append(result)

    # Summary
    migration_record["completed_at"] = datetime.now().isoformat()
    migration_record["overall_success"] = all(r.get("success") for r in migration_record["results"])

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"MIGRATION COMPLETE", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    success_count = sum(1 for r in migration_record["results"] if r.get("success"))
    print(f"\nEpisodes migrated: {success_count}/{len(episodes)}", file=sys.stderr)

    for result in migration_record["results"]:
        status = "OK" if result.get("success") else "PARTIAL"
        print(f"  Episode {result['episode']}: [{status}]", file=sys.stderr)
        if result.get("error"):
            print(f"    Error: {result['error']}", file=sys.stderr)

    # Save log
    if not args.dry_run:
        log = load_migration_log()
        log["migrations"].append(migration_record)
        save_migration_log(log)
        print(f"\nMigration log saved to: {MIGRATION_LOG}", file=sys.stderr)

    print()


if __name__ == "__main__":
    main()
