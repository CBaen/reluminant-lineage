#!/usr/bin/env python3
"""
conversation-indexer.py - Main orchestrator for conversation log indexing

Coordinates the full pipeline:
1. Reads state (what's been indexed)
2. Finds new/updated conversations
3. Parses → Classifies → Summarizes → Stores to Qdrant
4. Updates state

Usage:
    # Index new conversations
    python conversation-indexer.py

    # Index a specific session
    python conversation-indexer.py --session-id abc123

    # Re-index everything (ignore state)
    python conversation-indexer.py --reindex

    # Dry run (show what would be indexed)
    python conversation-indexer.py --dry-run

    # Use specific Gemini account
    python conversation-indexer.py --account 2

Part of the Conversation Log Indexer system.
Created: January 2026 by the Lineage
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.expanduser("~/.claude/conversation-index-state.json")
PROJECTS_DIR = os.path.expanduser("~/.claude/projects")
QDRANT_URL = "http://localhost:6333"
COLLECTION = "universal_vault"


@dataclass
class IndexState:
    """Tracks what has been indexed."""
    version: str = "1.0"
    last_run: Optional[str] = None
    indexed_sessions: Dict[str, dict] = None  # session_id -> {file_path, indexed_at, message_count}
    total_exchanges_indexed: int = 0
    total_sessions_indexed: int = 0

    def __post_init__(self):
        if self.indexed_sessions is None:
            self.indexed_sessions = {}


def load_state() -> IndexState:
    """Load indexing state from file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return IndexState(
                    version=data.get('version', '1.0'),
                    last_run=data.get('last_run'),
                    indexed_sessions=data.get('indexed_sessions', {}),
                    total_exchanges_indexed=data.get('total_exchanges_indexed', 0),
                    total_sessions_indexed=data.get('total_sessions_indexed', 0)
                )
        except Exception as e:
            print(f"Warning: Could not load state: {e}", file=sys.stderr)
    return IndexState()


def save_state(state: IndexState):
    """Save indexing state to file."""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(asdict(state), f, indent=2, default=str)
    except Exception as e:
        print(f"Warning: Could not save state: {e}", file=sys.stderr)


def find_session_files(
    directory: Path,
    include_agents: bool = False
) -> List[Path]:
    """Find all session JSONL files."""
    sessions = []

    for jsonl_file in directory.rglob("*.jsonl"):
        filename = jsonl_file.name

        # Skip agent files by default
        if not include_agents and filename.startswith("agent-"):
            continue

        # Skip history files
        if filename == "history.jsonl":
            continue

        sessions.append(jsonl_file)

    return sessions


def get_file_info(file_path: Path) -> dict:
    """Get file metadata for change detection."""
    stat = file_path.stat()
    return {
        "size": stat.st_size,
        "mtime": stat.st_mtime,
        "path": str(file_path)
    }


def needs_indexing(
    file_path: Path,
    state: IndexState,
    force: bool = False
) -> bool:
    """Check if a session file needs (re)indexing."""
    if force:
        return True

    session_id = file_path.stem
    if session_id not in state.indexed_sessions:
        return True

    # Check if file was modified since last index
    indexed_info = state.indexed_sessions[session_id]
    current_info = get_file_info(file_path)

    # Re-index if file size changed or was modified
    if current_info["size"] != indexed_info.get("size"):
        return True
    if current_info["mtime"] > indexed_info.get("indexed_at_timestamp", 0):
        return True

    return False


def import_parser():
    """Import conversation parser module."""
    from importlib.util import spec_from_file_location, module_from_spec
    parser_path = os.path.join(SCRIPT_DIR, "conversation-parser.py")
    spec = spec_from_file_location("conv_parser", parser_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_classifier():
    """Import conversation classifier module."""
    from importlib.util import spec_from_file_location, module_from_spec
    classifier_path = os.path.join(SCRIPT_DIR, "conversation-classifier.py")
    spec = spec_from_file_location("conv_classifier", classifier_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_summarizer():
    """Import conversation summarizer module."""
    from importlib.util import spec_from_file_location, module_from_spec
    summarizer_path = os.path.join(SCRIPT_DIR, "conversation-summarizer.py")
    spec = spec_from_file_location("conv_summarizer", summarizer_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def store_to_qdrant(data: dict, session: str) -> bool:
    """Store summarized data to Qdrant via qdrant-store-gemini.py."""
    store_script = os.path.join(SCRIPT_DIR, "qdrant-store-gemini.py")

    try:
        proc = subprocess.run(
            [sys.executable, store_script, "--collection", COLLECTION, "--session", session, "--hybrid"],
            input=json.dumps(data),
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for large batches
        )

        if proc.returncode == 0:
            try:
                result = json.loads(proc.stdout)
                return result.get("success", False)
            except:
                return True  # Assume success if can't parse
        else:
            print(f"Storage error: {proc.stderr}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"Storage subprocess error: {e}", file=sys.stderr)
        return False


def index_session(
    file_path: Path,
    account: int = 1,
    no_gemini: bool = False,
    batch_size: int = 10,
    verbose: bool = False
) -> Optional[dict]:
    """
    Index a single session file.

    Returns:
        Dict with indexing results or None on failure
    """
    parser = import_parser()
    classifier = import_classifier()
    summarizer = import_summarizer()

    # Step 1: Parse
    if verbose:
        print(f"  Parsing {file_path.name}...", file=sys.stderr)

    session = parser.parse_session_file(file_path)
    if not session:
        return {"error": "Parse failed", "file": str(file_path)}

    parsed = asdict(session)

    # Step 2: Classify
    if verbose:
        print(f"  Classifying {session.message_count} messages...", file=sys.stderr)

    exchanges = classifier.classify_session(
        parsed,
        min_length=50,
        min_messages=2
    )

    if not exchanges:
        return {
            "skipped": True,
            "reason": "No indexable exchanges",
            "session_id": session.session_id,
            "message_count": session.message_count
        }

    # Convert to dicts for JSON
    exchanges_data = [asdict(ex) for ex in exchanges]

    if verbose:
        print(f"  Found {len(exchanges_data)} indexable exchanges", file=sys.stderr)

    # Step 3: Summarize
    if verbose:
        print(f"  Summarizing with Gemini..." if not no_gemini else "  Using fallback summarizer...", file=sys.stderr)

    if no_gemini:
        summaries = [summarizer.fallback_summarize(exchanges_data, session.session_id)]
    else:
        summaries = summarizer.batch_summarize(
            exchanges_data,
            session.session_id,
            session.summary,
            batch_size=batch_size,
            account=account
        )

    if not summaries:
        return {
            "error": "Summarization failed",
            "session_id": session.session_id,
            "exchanges_found": len(exchanges_data)
        }

    # Step 4: Store to Qdrant
    if verbose:
        print(f"  Storing {len(summaries)} batch(es) to Qdrant...", file=sys.stderr)

    stored_count = 0
    chunk_count = 0
    for summary_batch in summaries:
        if store_to_qdrant(summary_batch, f"conversation-index-{session.session_id}"):
            stored_count += 1
            chunk_count += len(summary_batch.get('chunks', []))

    return {
        "success": stored_count > 0,
        "session_id": session.session_id,
        "file_path": str(file_path),
        "message_count": session.message_count,
        "exchanges_found": len(exchanges_data),
        "batches_stored": stored_count,
        "chunks_indexed": chunk_count,
        "session_summary": session.summary
    }


def main():
    parser = argparse.ArgumentParser(
        description="Index conversation logs for searchability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Index new conversations
    python conversation-indexer.py

    # Re-index everything
    python conversation-indexer.py --reindex

    # Dry run to see what would be indexed
    python conversation-indexer.py --dry-run

    # Index without Gemini (faster, lower quality)
    python conversation-indexer.py --no-gemini

    # Index a specific session
    python conversation-indexer.py --session-id 7fffc65b-fb79-4d6a-b051-b7d85a529e63
        """
    )

    parser.add_argument("--session-id", help="Index a specific session")
    parser.add_argument("--reindex", action="store_true",
                        help="Re-index all sessions (ignore state)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be indexed")
    parser.add_argument("-a", "--account", type=int, default=1, choices=[1, 2],
                        help="Gemini account (default: 1)")
    parser.add_argument("--no-gemini", action="store_true",
                        help="Use fallback summarizer (no AI)")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Exchanges per Gemini call")
    parser.add_argument("--include-agents", action="store_true",
                        help="Include agent session files")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")
    parser.add_argument("--projects-dir", type=Path, default=Path(PROJECTS_DIR),
                        help="Projects directory")
    parser.add_argument("--status", action="store_true",
                        help="Show indexing status and exit")

    args = parser.parse_args()

    # Load state
    state = load_state()

    # Status mode
    if args.status:
        print(f"Conversation Index Status")
        print(f"=" * 40)
        print(f"State file: {STATE_FILE}")
        print(f"Last run: {state.last_run or 'Never'}")
        print(f"Sessions indexed: {state.total_sessions_indexed}")
        print(f"Total exchanges: {state.total_exchanges_indexed}")
        print(f"\nRecently indexed:")
        for sid, info in list(state.indexed_sessions.items())[-5:]:
            print(f"  - {sid[:8]}... ({info.get('exchanges_indexed', 0)} exchanges)")
        return

    # Find sessions to index
    if args.session_id:
        # Find specific session
        session_files = list(args.projects_dir.rglob(f"*{args.session_id}*.jsonl"))
        if not session_files:
            print(f"Session not found: {args.session_id}")
            sys.exit(1)
    else:
        session_files = find_session_files(args.projects_dir, args.include_agents)

    # Filter to sessions needing indexing
    to_index = []
    for f in session_files:
        if needs_indexing(f, state, force=args.reindex or args.session_id):
            to_index.append(f)

    print(f"Found {len(to_index)} session(s) to index (of {len(session_files)} total)")

    if not to_index:
        print("Nothing to index.")
        return

    if args.dry_run:
        print("\nDry run - would index:")
        for f in to_index[:20]:
            print(f"  - {f.stem}")
        if len(to_index) > 20:
            print(f"  ... and {len(to_index) - 20} more")
        return

    # Index sessions
    results = []
    for i, file_path in enumerate(to_index, 1):
        print(f"\n[{i}/{len(to_index)}] Indexing {file_path.stem}...")

        result = index_session(
            file_path,
            account=args.account,
            no_gemini=args.no_gemini,
            batch_size=args.batch_size,
            verbose=args.verbose
        )

        if result:
            results.append(result)

            # Update state on success
            if result.get('success'):
                file_info = get_file_info(file_path)
                state.indexed_sessions[result['session_id']] = {
                    "file_path": str(file_path),
                    "indexed_at": datetime.now().isoformat(),
                    "indexed_at_timestamp": datetime.now().timestamp(),
                    "size": file_info["size"],
                    "mtime": file_info["mtime"],
                    "message_count": result.get('message_count', 0),
                    "exchanges_indexed": result.get('exchanges_found', 0),
                    "chunks_indexed": result.get('chunks_indexed', 0)
                }
                state.total_sessions_indexed += 1
                state.total_exchanges_indexed += result.get('exchanges_found', 0)

                print(f"  Done: {result.get('exchanges_found', 0)} exchanges indexed")
            elif result.get('skipped'):
                print(f"  Skipped: {result.get('reason')}")
            else:
                print(f"  Failed: {result.get('error', 'Unknown error')}")

    # Save state
    state.last_run = datetime.now().isoformat()
    save_state(state)

    # Summary
    successful = sum(1 for r in results if r.get('success'))
    skipped = sum(1 for r in results if r.get('skipped'))
    failed = sum(1 for r in results if r.get('error'))
    total_exchanges = sum(r.get('exchanges_found', 0) for r in results if r.get('success'))

    print(f"\n{'=' * 40}")
    print(f"Indexing Complete")
    print(f"  Successful: {successful}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Total exchanges indexed: {total_exchanges}")
    print(f"\nState saved to: {STATE_FILE}")


if __name__ == "__main__":
    main()
