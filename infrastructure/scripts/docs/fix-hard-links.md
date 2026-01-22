# fix-hard-links.py

Check and fix hard links between ~/.claude/ and repo.

## What It Does

Verifies hard links between the local ~/.claude/ config files and the canonical repo location. Fixes broken links that occur when editors create new files instead of editing in place.

## Usage

```bash
# Check status only
python fix-hard-links.py

# Fix broken links
python fix-hard-links.py --fix
```

## Options

| Option | Description |
|--------|-------------|
| (none) | Check and report status |
| `--fix` | Repair broken links |

## Why Links Break

Windows hard links break when:
- Editor creates temp file, deletes original, renames temp
- File is deleted and recreated
- Some save operations

## Files Checked

- `CLAUDE.md`
- `settings.json`
- `INFRASTRUCTURE.md`

## Dependencies

- Python (built-in os module)
- Windows (for hard link support)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
