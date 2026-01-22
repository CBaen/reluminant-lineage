# conversation-indexer.py

Main orchestrator for conversation log indexing.

## What It Does

Coordinates the full pipeline for indexing Claude Code conversation logs: parsing, classifying, summarizing, and storing to Qdrant for later retrieval.

## Usage

```bash
# Index new conversations
python conversation-indexer.py

# Index specific session
python conversation-indexer.py --session-id abc123

# Re-index all
python conversation-indexer.py --reindex

# Preview without storing
python conversation-indexer.py --dry-run

# Use specific Gemini account
python conversation-indexer.py --account 2
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--session-id` | Specific session to index | All new |
| `--reindex` | Re-index all sessions | False |
| `--dry-run` | Preview without storing | False |
| `--account` | Gemini account for summarization | 1 |

## Pipeline

1. **Parse** - Extract messages from JSONL logs
2. **Classify** - Categorize content type
3. **Summarize** - Generate summary via Gemini
4. **Store** - Save to Qdrant with embeddings

## Dependencies

- `conversation-parser.py`
- `conversation-classifier.py`
- `conversation-summarizer.py`
- `qdrant-client`
- Gemini API

## Changelog

- 2026-01-20: Initial creation (59ef471)
- 2026-01-19: Infrastructure consolidation (39a41dc)
