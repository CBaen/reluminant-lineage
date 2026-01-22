# gemini-swarm-worker.sh

Swarm worker with account locking.

## What It Does

Individual worker for swarm-based parallel research. Implements account locking to prevent conflicts when multiple workers run simultaneously.

## Usage

```bash
gemini-swarm-worker.sh "topic" "perspective" "collection" "session" "depth"
```

## Arguments

| Position | Description |
|----------|-------------|
| 1 | Research topic |
| 2 | Perspective/angle |
| 3 | Target collection |
| 4 | Session identifier |
| 5 | Research depth |

## Account Locking

- Acquires lock before API call
- Releases lock after completion
- Prevents rate limit collisions

## Dependencies

- Bash shell
- Lock file system
- Gemini API credentials

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
