# research-pipeline.sh

Full research pipeline with dual storage (Qdrant + catalog).

## What It Does

Complete research workflow that checks existing knowledge before querying Gemini, then stores results to both Qdrant (vector) and catalog (flat files).

## Usage

```bash
research-pipeline.sh "topic" "question" "session" ["tags"]
```

## Arguments

| Position | Description | Required |
|----------|-------------|----------|
| 1 | Topic name | Yes |
| 2 | Research question | Yes |
| 3 | Session identifier | Yes |
| 4 | Comma-separated tags | No |

## Pipeline Steps

1. Check Qdrant (semantic search)
2. Check catalog (flat files)
3. If found: returns path(s)
4. If not found: queries Gemini
5. Stores to BOTH Qdrant and catalog

## Output

- Returns existing file path if found
- Returns new file path if created
- Exits with error if Gemini fails

## Dependencies

- Bash shell
- Qdrant server
- Gemini API
- Catalog directory structure

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
