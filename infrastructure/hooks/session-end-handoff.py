#!/usr/bin/env python3
"""
Session End Handoff Hook - Queues transcripts for async Qdrant storage.

This hook receives {session_id, transcript_path} from stdin when a session ends.
It writes to a queue file and spawns the worker asynchronously, then exits immediately.
The actual heavy lifting (parsing, embedding, storing) happens in the background.

Usage in settings.json:
  "SessionEnd": [{
    "hooks": [{
      "type": "command",
      "command": "python C:/Users/baenb/.claude/hooks/session-end-handoff.py"
    }]
  }]
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

CLAUDE_DIR = Path.home() / ".claude"
QUEUE_FILE = CLAUDE_DIR / "hooks" / "handoff-queue.jsonl"
WORKER_SCRIPT = CLAUDE_DIR / "hooks" / "handoff-worker.py"
WORKER_LOG = CLAUDE_DIR / "hooks" / "worker.log"

def main():
    try:
        # Read JSON from stdin (Claude Code sends {session_id, transcript_path})
        input_data = sys.stdin.read().strip()
        if not input_data:
            return  # No input, exit silently

        data = json.loads(input_data)
        session_id = data.get("session_id", "unknown")
        transcript_path = data.get("transcript_path", "")

        if not transcript_path or not Path(transcript_path).exists():
            return  # No transcript, exit silently

        # Queue entry with metadata
        queue_entry = {
            "session_id": session_id,
            "transcript_path": transcript_path,
            "queued_at": datetime.now().isoformat(),
            "status": "pending"
        }

        # Append to queue file
        QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUEUE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(queue_entry) + "\n")

        # Spawn worker asynchronously (detached from this process)
        # On Windows, use CREATE_NO_WINDOW to hide console
        if os.name == 'nt':
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(
                [sys.executable, str(WORKER_SCRIPT)],
                stdout=open(WORKER_LOG, "a"),
                stderr=subprocess.STDOUT,
                creationflags=CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                close_fds=True
            )
        else:
            # Unix: use nohup-style background
            subprocess.Popen(
                [sys.executable, str(WORKER_SCRIPT)],
                stdout=open(WORKER_LOG, "a"),
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True
            )

        # Exit immediately - don't block CLI

    except Exception as e:
        # Log error but don't block CLI
        try:
            with open(WORKER_LOG, "a") as f:
                f.write(f"[{datetime.now().isoformat()}] Hook error: {e}\n")
        except:
            pass

if __name__ == "__main__":
    main()
