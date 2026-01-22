# qdrant-code-index.py

Index Python code for semantic search.

## What It Does

Scans a codebase, extracts functions and classes with their docstrings, embeds them, and stores to Qdrant. Tracks commit hash to avoid re-indexing unchanged files.

## Usage

```bash
# Index a project
python qdrant-code-index.py --path /project --collection code_index

# Exclude directories
python qdrant-code-index.py --path . --exclude "venv,node_modules"
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--path` | Directory to index | Required |
| `--collection` | Target collection | code_index |
| `--exclude` | Comma-separated dirs to exclude | - |

## What Gets Indexed

- Function definitions with docstrings
- Class definitions with docstrings
- Module-level docstrings
- File path and line numbers for navigation

## Dependencies

- `qdrant-client`
- Ollama (for embeddings)
- Python AST parser (built-in)
- Git (for commit tracking)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
