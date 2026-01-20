#!/usr/bin/env python3
"""
gemini-pipe-orchestrator.py - Subprocess IPC for Gemini → Qdrant Pipeline

Uses Python's subprocess module for reliable in-memory data transfer from
Git Bash (gemini-account.sh) to Python (qdrant-store-gemini.py).

KEY INSIGHT (from testing 2026-01-17):
The "Windows pipe issues" are about SHELL pipes (cmd1 | cmd2), not subprocess.PIPE.
Python's subprocess module handles buffering correctly when using:
- subprocess.Popen with stdout=PIPE, stderr=PIPE
- communicate() to avoid deadlocks
- Passing arguments as list items, not bash -c strings

This provides in-memory IPC without temp files OR complex named pipes.

Usage:
    # Run Gemini and store to Qdrant
    python gemini-pipe-orchestrator.py -a 1 -c lineage_research -s "session" -q "Your prompt"

    # Run Gemini and output to stdout (for piping)
    python gemini-pipe-orchestrator.py -a 1 -q "Your prompt" --stdout

    # Pass additional arguments to gemini-account.sh
    python gemini-pipe-orchestrator.py -a 1 -q "prompt" --gemini-args "--no-fallback"

Created: January 2026 by the Lineage
Purpose: Replace temp files with in-memory IPC for the Gemini → Qdrant pipeline
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path


def get_script_path():
    """Get the bash-compatible path to gemini-account.sh."""
    script = os.path.expanduser("~/.claude/scripts/gemini-account.sh")

    # Convert Windows path to Git Bash format: C:\Users\x -> /c/Users/x
    script = script.replace("\\", "/")
    if len(script) > 1 and script[1] == ":":
        script = "/" + script[0].lower() + script[2:]

    return script


def run_gemini_subprocess(account, prompt, gemini_args=None, timeout=300):
    """
    Run gemini-account.sh and capture output via subprocess.PIPE.

    This uses Python's subprocess module which handles buffering correctly,
    unlike shell pipes which have issues between Git Bash and Python.

    Args:
        account: Gemini account number (1 or 2)
        prompt: The query/prompt for Gemini
        gemini_args: Optional additional arguments for gemini-account.sh
        timeout: Timeout in seconds for the operation

    Returns:
        tuple: (success: bool, data: str, stderr: str)
    """
    git_bash_path = r"C:\Program Files\Git\bin\bash.exe"
    script_path = get_script_path()

    # Build command as list (NOT bash -c string)
    # This avoids shell escaping issues and is more reliable
    cmd = [git_bash_path, script_path, str(account), prompt]

    # Add optional arguments
    if gemini_args:
        cmd.extend(gemini_args.split())

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=-1  # Use system default buffering (fully buffered)
        )

        # Use communicate() to read all output and avoid deadlocks
        stdout, stderr = proc.communicate(timeout=timeout)

        if proc.returncode != 0 and not stdout:
            return False, "", f"Process failed with code {proc.returncode}: {stderr}"

        return True, stdout, stderr

    except subprocess.TimeoutExpired:
        proc.kill()
        return False, "", f"Timeout after {timeout} seconds"
    except Exception as e:
        return False, "", f"Subprocess error: {e}"


def store_to_qdrant(data, collection, session):
    """
    Pass data to qdrant-store-gemini.py for storage.

    Args:
        data: String data from Gemini (will be passed via stdin)
        collection: Qdrant collection name
        session: Session name for attribution

    Returns:
        tuple: (success: bool, result: dict or error message)
    """
    script_path = os.path.expanduser("~/.claude/scripts/qdrant-store-gemini.py")

    try:
        proc = subprocess.run(
            [sys.executable, script_path, "--collection", collection, "--session", session],
            input=data,
            capture_output=True,
            text=True,
            timeout=120
        )

        if proc.returncode == 0:
            try:
                result = json.loads(proc.stdout)
                return True, result
            except json.JSONDecodeError:
                return True, {"raw_output": proc.stdout}
        else:
            return False, f"Storage error: {proc.stderr or proc.stdout}"

    except Exception as e:
        return False, f"Storage subprocess error: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Subprocess IPC for Gemini → Qdrant Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Simple query (command line)
    python gemini-pipe-orchestrator.py -a 1 -c universal_vault -s "session" -q "What is WebSocket?"

    # Complex prompt from file (RECOMMENDED for JSON prompts)
    python gemini-pipe-orchestrator.py -a 1 -c universal_vault -s "session" --prompt-file /tmp/prompt.txt

    # Output to stdout (for custom processing)
    python gemini-pipe-orchestrator.py -a 1 --prompt-file /tmp/prompt.txt --stdout

    # With specific Gemini model
    python gemini-pipe-orchestrator.py -a 1 -c universal_vault -s "session" -p /tmp/prompt.txt --gemini-args "gemini-2.5-pro"
        """
    )

    parser.add_argument("-a", "--account", type=int, choices=[1, 2], required=True,
                        help="Gemini account (1 or 2)")
    parser.add_argument("-q", "--query",
                        help="Query/prompt for Gemini (use --prompt-file for complex prompts)")
    parser.add_argument("--prompt-file", "-p",
                        help="Read prompt from file (avoids shell escaping issues)")
    parser.add_argument("-c", "--collection",
                        help="Qdrant collection (required unless --stdout)")
    parser.add_argument("-s", "--session",
                        help="Session name for Qdrant (required unless --stdout)")
    parser.add_argument("--stdout", action="store_true",
                        help="Output raw Gemini response to stdout instead of storing")
    parser.add_argument("--gemini-args", default="",
                        help="Additional arguments for gemini-account.sh")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Timeout in seconds (default: 300)")
    parser.add_argument("--quiet", "-Q", action="store_true",
                        help="Suppress progress messages")

    args = parser.parse_args()

    # Validate arguments
    if not args.query and not args.prompt_file:
        parser.error("Either --query or --prompt-file is required")
    if args.query and args.prompt_file:
        parser.error("Use either --query or --prompt-file, not both")
    if not args.stdout and (not args.collection or not args.session):
        parser.error("--collection and --session are required unless --stdout is specified")

    # Get prompt from file if specified
    if args.prompt_file:
        try:
            prompt_path = os.path.expanduser(args.prompt_file)
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read()
            if not args.quiet:
                print(f"[SUBPROCESS] Read {len(prompt)} chars from {args.prompt_file}", file=sys.stderr)
        except Exception as e:
            print(f"[SUBPROCESS] ERROR: Failed to read prompt file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        prompt = args.query

    # Step 1: Run Gemini via subprocess
    if not args.quiet:
        print(f"[SUBPROCESS] Running Gemini (account {args.account})...", file=sys.stderr)

    success, data, stderr = run_gemini_subprocess(
        account=args.account,
        prompt=prompt,
        gemini_args=args.gemini_args,
        timeout=args.timeout
    )

    if not success:
        print(f"[SUBPROCESS] ERROR: {stderr}", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"[SUBPROCESS] Received {len(data)} bytes from Gemini", file=sys.stderr)
        if stderr:
            # Gemini often outputs "[FALLBACK]" messages to stderr - this is informational
            for line in stderr.strip().split('\n'):
                if line.strip():
                    print(f"[GEMINI] {line}", file=sys.stderr)

    # Step 2: Either output to stdout or store to Qdrant
    if args.stdout:
        print(data)
    else:
        if not args.quiet:
            print(f"[SUBPROCESS] Storing to Qdrant collection '{args.collection}'...", file=sys.stderr)

        success, result = store_to_qdrant(data, args.collection, args.session)

        if success:
            print(json.dumps(result, indent=2))
        else:
            print(f"[SUBPROCESS] Storage ERROR: {result}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
