# qdrant-store-gemini.py

Store Gemini's self-chunked research output directly.

## What It Does

Takes Gemini's structured JSON output (with meta, summary, and chunks array) and stores it to Qdrant. Supports both V1 (legacy) and V2 (hybrid) schemas.

## Usage

```bash
echo '{"meta": {...}, "chunks": [...]}' | python qdrant-store-gemini.py \
  --hybrid \
  --session "my-session"
```

## Input Format

Gemini JSON with:
- `meta` - Metadata object
- `summary` - Top-level summary
- `chunks` - Array of content chunks

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--hybrid` | Use V2 hybrid schema | False |
| `--session` | Session identifier | - |
| `--collection` | Target collection | universal_vault |

## Output

JSON with storage results including point IDs.

## Dependencies

- `qdrant-client`
- Ollama (for embeddings)
- `fastembed` (for sparse embeddings in hybrid mode)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
