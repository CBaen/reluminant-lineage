# store-rag-research.py

Store RAG research results to Qdrant.

## What It Does

Takes RAG (Retrieval-Augmented Generation) research output and stores it to Qdrant with appropriate chunking and metadata.

## Usage

```bash
cat rag-output.json | python store-rag-research.py --session "session-id"
```

## Input Format

JSON with RAG research structure including sources and synthesized content.

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--session` | Session identifier | Required |
| `--collection` | Target collection | universal_vault |

## Dependencies

- `qdrant-client`
- Ollama (embeddings)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
