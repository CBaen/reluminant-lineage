# gemini-research-direct.py

Direct research without daemon overhead.

## What It Does

Performs a single research query directly without going through the daemon. Useful for one-off queries or debugging.

## Usage

```bash
python gemini-research-direct.py --query "Your research topic"
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--query` | Research query | Required |
| `--account` | Account number | 1 |
| `--store` | Store to Qdrant | True |

## When to Use

- Single queries that don't need queuing
- Testing and debugging
- When daemon is not running

## Dependencies

- `google-generativeai`
- `qdrant-client` (if storing)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
