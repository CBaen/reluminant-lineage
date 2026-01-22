# doc-audit.py

Audit documentation for duplicates and structure.

## What It Does

Scans documentation files across the project, identifies potential duplicates, and reports on documentation structure and coverage.

## Usage

```bash
python doc-audit.py
```

## Output

JSON report containing:
- File inventory
- Potential duplicates (by content similarity)
- Coverage gaps
- Structure analysis

## Report Location

`doc-audit-report.json` in same directory.

## Dependencies

- None (pure Python)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
