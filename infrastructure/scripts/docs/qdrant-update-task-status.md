# qdrant-update-task-status.py

Update task metadata without re-embedding.

## What It Does

Updates the status and metadata fields of existing Qdrant points without regenerating embeddings. Useful for tracking task progress in project management workflows.

## Usage

```bash
python qdrant-update-task-status.py --collection "project" \
  --point-id "uuid" --phase 1 --task 1 --status "completed"
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--collection` | Collection name | Required |
| `--point-id` | UUID of point to update | Required |
| `--phase` | Phase number | - |
| `--task` | Task number | - |
| `--status` | New status | Required |

## Status Values

- `pending` - Not yet started
- `in_progress` - Currently being worked on
- `completed` - Finished successfully
- `blocked` - Waiting on external dependency

## Dependencies

- `qdrant-client`

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
