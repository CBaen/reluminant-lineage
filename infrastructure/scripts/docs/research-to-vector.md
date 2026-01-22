# research-to-vector.py

Query Gemini and store directly to Qdrant.

## What It Does

Single-step script that queries Gemini for research and immediately stores the result to Qdrant. Simpler than the full pipeline when you just need vector storage.

## Usage

```bash
python research-to-vector.py "topic" "question" "domain" "tag1,tag2"
```

## Arguments

| Position | Description |
|----------|-------------|
| 1 | Topic name |
| 2 | Research question |
| 3 | Domain/project |
| 4 | Comma-separated tags |

## Output

JSON with:
- `point_id` - Qdrant point UUID
- `chunks` - Number of chunks stored

## Dependencies

- `google-generativeai`
- `qdrant-client`
- Ollama (embeddings)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
