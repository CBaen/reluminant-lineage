# qdrant-semantic-search.py

Semantic search with V2 hybrid support.

## What It Does

Performs semantic search against Qdrant collections, supporting both dense-only and hybrid (dense + sparse) search modes. Hybrid search combines vector similarity with keyword matching for better results.

## Usage

```bash
# Hybrid search (recommended)
python qdrant-semantic-search.py --hybrid --query "how does caching work"

# Filter by importance
python qdrant-semantic-search.py --hybrid --query "caching" --importance core

# Show full content
python qdrant-semantic-search.py --hybrid --query "caching" --full
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--query` | Search query | Required |
| `--hybrid` | Enable hybrid search (dense + sparse) | False |
| `--collection` | Collection | universal_vault |
| `--importance` | Filter: core/supporting/advanced | - |
| `--keywords` | Filter by keywords | - |
| `--full` | Show full content and questions_answered | False |
| `--limit` | Max results | 5 |

## Dependencies

- `qdrant-client`
- Ollama (for dense embeddings)
- `fastembed` (for sparse embeddings in hybrid mode)

## Changelog

- 2026-01-19: Fix stale references (ffd1bb5)
- 2026-01-19: Initial consolidation into repo (39a41dc)
