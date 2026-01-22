# catalog-lookup.sh

Find research by topic.

## What It Does

Searches the flat-file research catalog for a specific topic and returns the file path if found.

## Usage

```bash
catalog-lookup.sh "topic"
```

## Output

- File path if found: `/path/to/research/topic.md`
- `NOT_FOUND` if not found

## Side Effects

Updates access metadata (last accessed timestamp) when file is found, affecting tier rotation.

## Dependencies

- Bash shell
- Catalog directory structure

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
