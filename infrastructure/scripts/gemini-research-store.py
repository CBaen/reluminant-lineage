#!/usr/bin/env python3
"""
gemini-research-store.py - Windows-compatible Gemini research pipeline

This script solves the Windows pipe issue by:
1. Running gemini-account.sh and capturing output to a temp file
2. Passing that file to qdrant-store-gemini.py via --input-file

Usage:
    python gemini-research-store.py --account 1 --collection lineage_research --session my-session --query "Your research query"

This replaces the Unix-style:
    gemini-account.sh 1 'query' | python qdrant-store-gemini.py --collection X --session Y

Which doesn't work on Windows due to pipe handling issues.
"""

import argparse
import subprocess
import sys
import os
import tempfile
import json
from pathlib import Path


def get_script_dir():
    """Get the directory where this script lives."""
    return Path(__file__).parent.resolve()


def find_git_bash():
    """Find Git Bash on Windows, avoiding WSL bash."""
    candidates = [
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\usr\bin\bash.exe",
        os.path.expandvars(r"%PROGRAMFILES%\Git\usr\bin\bash.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # Fallback to "bash" and hope for the best
    return "bash"


def run_gemini(account: int, query: str, model: str = "gemini-2.5-flash") -> str:
    """Run gemini-account.sh and return output."""
    script_path = get_script_dir() / "gemini-account.sh"

    # Use Git Bash explicitly (not WSL bash)
    bash_path = find_git_bash()
    cmd = [bash_path, str(script_path), str(account), query, model]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for research queries
            encoding='utf-8',
            errors='replace'
        )

        # Combine stdout and filter stderr noise
        output = result.stdout

        # Log any actual errors (not just "Loaded cached credentials")
        stderr_lines = [l for l in result.stderr.split('\n')
                       if l.strip() and 'Loaded cached credentials' not in l]
        if stderr_lines:
            print(f"Gemini stderr: {'; '.join(stderr_lines)}", file=sys.stderr)

        return output

    except subprocess.TimeoutExpired:
        print("Error: Gemini query timed out after 5 minutes", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Error running Gemini: {e}", file=sys.stderr)
        return ""


def store_to_qdrant(gemini_output: str, collection: str, session: str) -> dict:
    """Store Gemini output to Qdrant using temp file approach."""
    if not gemini_output.strip():
        return {"error": "Empty Gemini output", "success": False}

    script_path = get_script_dir() / "qdrant-store-gemini.py"

    # Write to temp file (solves Windows pipe issue)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        f.write(gemini_output)
        temp_path = f.name

    try:
        cmd = [
            sys.executable,  # Use the same Python interpreter
            str(script_path),
            "--collection", collection,
            "--session", session,
            "--input-file", temp_path,
            "--hybrid"  # Always use hybrid for new storage
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )

        # Try to parse the output as JSON
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse storage result",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": False
            }

    except Exception as e:
        return {"error": str(e), "success": False}
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Windows-compatible Gemini research pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic research query
    python gemini-research-store.py -a 1 -c lineage_research -s my-session -q "Research OAuth patterns"

    # With custom model
    python gemini-research-store.py -a 2 -c project_research -s feature-x -q "Your query" -m gemini-2.5-pro
        """
    )

    parser.add_argument("-a", "--account", type=int, required=True, choices=[1, 2],
                       help="Gemini account to use (1 or 2)")
    parser.add_argument("-c", "--collection", default="universal_vault",
                       help="Qdrant collection name (default: universal_vault)")
    parser.add_argument("--hybrid", action="store_true",
                       help="Use hybrid storage (dense + sparse vectors) - RECOMMENDED")
    parser.add_argument("-s", "--session", required=True,
                       help="Session name for attribution")
    parser.add_argument("-q", "--query", required=True,
                       help="The query/prompt to send to Gemini")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash",
                       help="Gemini model to use")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run Gemini but don't store to Qdrant (for testing)")

    args = parser.parse_args()

    # Step 1: Run Gemini
    print(f"Querying Gemini (account {args.account})...", file=sys.stderr)
    gemini_output = run_gemini(args.account, args.query, args.model)

    if not gemini_output.strip():
        print(json.dumps({"error": "No output from Gemini", "success": False}))
        sys.exit(1)

    if args.dry_run:
        print("=== DRY RUN - Gemini output ===")
        print(gemini_output)
        print("=== End dry run ===")
        sys.exit(0)

    # Step 2: Store to Qdrant
    print(f"Storing to Qdrant ({args.collection})...", file=sys.stderr)
    result = store_to_qdrant(gemini_output, args.collection, args.session)

    # Output result
    print(json.dumps(result, indent=2))

    if result.get("success"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
