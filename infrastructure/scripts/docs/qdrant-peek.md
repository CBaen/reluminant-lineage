# qdrant-peek.py

Token-efficient two-stage Qdrant retrieval.

## What It Does

Retrieves from Qdrant in two stages: peek (metadata only) then fetch (full content). Saves ~80% tokens vs fetching everything upfront.

## Usage

```bash
# Stage 1: Peek at metadata only (~50 tokens per result)
python qdrant-peek.py peek -q "OAuth" -l 5

# Stage 2: Fetch specific IDs
python qdrant-peek.py fetch --ids "uuid1,uuid2"
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `-q, --query` | Search query | Required |
| `-l, --limit` | Max results | 5 |
| `--collection` | Collection name | universal_vault |
| `--ids` | Comma-separated IDs (fetch mode) | - |

## Dependencies

- `qdrant-client`
- Ollama (for embeddings)
- Qdrant server running

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
