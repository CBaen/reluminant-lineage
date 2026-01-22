# gemini-research-store.py

Windows-compatible Gemini → Qdrant pipeline.

## What It Does

Complete pipeline that queries Gemini and stores results to Qdrant. Designed for Windows where Unix-style pipes fail.

## Usage

```bash
python gemini-research-store.py \
  --account 1 \
  --collection universal_vault \
  --session my-session \
  --query "Your research query"
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--account` | Gemini account (1 or 2) | Required |
| `--collection` | Target Qdrant collection | universal_vault |
| `--session` | Session identifier | - |
| `--query` | Research query | Required |
| `--hybrid` | Use V2 hybrid storage | False |

## Pipeline Steps

1. Format query with research prompt template
2. Call Gemini API
3. Validate and clean JSON response
4. Chunk content appropriately
5. Generate embeddings
6. Store to Qdrant

## Dependencies

- `google-generativeai`
- `qdrant-client`
- Ollama (embeddings)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
