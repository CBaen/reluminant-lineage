# gemini-research-daemon.py

Background research daemon for continuous processing.

## What It Does

Runs as a background daemon that processes research queries from a queue, handling rate limits and retries automatically.

## Usage

```bash
# Start daemon
python gemini-research-daemon.py start

# Stop daemon
python gemini-research-daemon.py stop

# Check status
python gemini-research-daemon.py status
```

## Features

- Queue-based processing
- Automatic rate limit handling
- Account rotation
- Retry with exponential backoff
- Logging to daemon.log

## Dependencies

- `google-generativeai`
- `qdrant-client`
- Queue file system

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
