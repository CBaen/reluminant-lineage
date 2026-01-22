# qdrant-chunked-store.py

Store research with proper chunking and parent-child linking.

## What It Does

Takes research content from stdin, chunks it intelligently, creates parent-child relationships, and stores to Qdrant with proper embeddings.

## Usage

```bash
cat research.json | python qdrant-chunked-store.py \
  --topic "topic-name" \
  --perspective "perspective-name" \
  --session "SessionName"
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--topic` | Topic identifier | Required |
| `--perspective` | Angle/perspective | general |
| `--session` | Session identifier for tracking | - |
| `--collection` | Target collection | universal_vault |

## Output

JSON with:
- `parent_id` - UUID of parent summary
- `chunks_stored` - Number of chunks created
- `total_words` - Word count
- `chunk_ids` - List of chunk UUIDs

## Dependencies

- `qdrant-client`
- Ollama (for embeddings)
- `qdrant_unified_schema.py`

## Changelog

- 2026-01-19: Fix stale references (ffd1bb5)
- 2026-01-19: Initial consolidation into repo (39a41dc)
