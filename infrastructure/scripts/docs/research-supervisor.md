# research-supervisor.py

Supervised research with progress tracking.

## What It Does

Wraps research queries with configuration, progress tracking, and logging. Provides visibility into long-running research tasks.

## Usage

```bash
python research-supervisor.py --query "topic" --depth comprehensive
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--query` | Research topic | Required |
| `--depth` | overview/comprehensive/exhaustive | comprehensive |
| `--account` | Gemini account | 1 |
| `--log` | Log file path | supervisor.log |

## Features

- Progress reporting
- Configurable depth
- Error recovery
- Detailed logging

## Dependencies

- `google-generativeai`
- `qdrant-client`

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
