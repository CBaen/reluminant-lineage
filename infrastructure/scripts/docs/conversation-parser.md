# conversation-parser.py

Parse conversation logs into structured format.

## What It Does

Reads Claude Code JSONL conversation logs and extracts structured message data for further processing.

## Usage

```python
from conversation_parser import parse_conversation

messages = parse_conversation("/path/to/transcript.jsonl")
```

## Output Structure

```python
[
    {
        "role": "user" | "assistant",
        "content": "message text",
        "timestamp": "ISO timestamp",
        "tool_calls": [...],  # if any
    }
]
```

## Handles

- JSONL format parsing
- Tool call extraction
- Timestamp normalization
- Malformed line recovery

## Dependencies

- None (pure Python)

## Changelog

- 2026-01-20: Initial creation (59ef471)
