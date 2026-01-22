# qdrant-migrate-collection.py

Migrate data from V1 to V2 schema.

## What It Does

Migrates existing Qdrant collections from the legacy V1 schema (single dense vector) to V2 schema (named vectors with dense + sparse). Re-embeds all content with sparse vectors.

## Usage

```bash
# Migrate a collection
python qdrant-migrate-collection.py --source legacy_collection

# With custom batch size
python qdrant-migrate-collection.py --source collection --batch 50
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--source` | Source collection name | Required |
| `--batch` | Batch size for processing | 100 |
| `--target` | Target collection | universal_vault |

## Migration Process

1. Reads points from source collection in batches
2. Extracts text content from payload
3. Generates sparse embeddings using fastembed
4. Creates new point with named vectors (dense + sparse)
5. Stores to target collection

## Dependencies

- `qdrant-client`
- Ollama (for dense re-embedding if needed)
- `fastembed` (for sparse embeddings)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
