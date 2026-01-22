# session-end-handoff.py

Queues transcripts for async Qdrant storage.

## What It Does

Fires on SessionEnd event. Receives session info from Claude Code, writes to queue file, and spawns the handoff worker asynchronously. Exits immediately to avoid blocking the CLI.

## Event

`SessionEnd`

## Input

JSON on stdin:
```json
{
  "session_id": "abc123",
  "transcript_path": "C:/Users/baenb/.claude/projects/.../transcript.jsonl"
}
```

## Behavior

1. Receives session data from stdin
2. Writes entry to `handoff-queue.jsonl`
3. Spawns `handoff-worker.py` asynchronously
4. Exits immediately (non-blocking)

## Configuration

In `settings.json`:
```json
{
  "hooks": {
    "SessionEnd": [{
      "type": "command",
      "command": "python C:/Users/baenb/.claude/hooks/session-end-handoff.py"
    }]
  }
}
```

## Dependencies

- Python standard library only
- `handoff-worker.py` for processing

## Changelog

- 2026-01-19: Moved from scripts/ to hooks/ (39a41dc)
