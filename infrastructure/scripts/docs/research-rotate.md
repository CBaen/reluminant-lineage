# research-rotate.sh

Usage-based tier rotation.

## What It Does

Moves research files between hot/warm/cold tiers based on access patterns. Keeps frequently accessed research readily available while archiving stale content.

## Usage

```bash
research-rotate.sh [--dry-run]
```

## Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would be moved without moving |

## Tier Rules

**Demotion:**
- hot → warm: 14+ days inactive
- warm → cold: 21+ days inactive

**Promotion:**
- Based on access frequency
- Recent access bumps tier up

## Tier Locations

- `hot/` - Frequently accessed, recent
- `warm/` - Occasionally accessed
- `cold/` - Archived, rarely needed

## Dependencies

- Bash shell
- File access timestamps

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
