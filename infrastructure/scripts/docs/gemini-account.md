# gemini-account.sh

Multi-account CLI wrapper with automatic model fallback.

## What It Does

Wraps Gemini API calls with multi-account support and automatic fallback through model tiers. Prioritizes quality over speed - starts with highest quality models and falls back through tiers until success.

## Usage

```bash
source ~/.claude/scripts/gemini-account.sh 1 "Your query"
source ~/.claude/scripts/gemini-account.sh 2 "Your query" gemini-2.5-pro
```

## Arguments

| Position | Description | Required |
|----------|-------------|----------|
| 1 | Account number (1 or 2) | Yes |
| 2 | Query/prompt | Yes |
| 3 | Model override | No |

## Fallback Chain

1. gemini-2.5-pro (Account 1)
2. gemini-2.5-pro (Account 2)
3. gemini-2.5-flash (Account 1)
4. gemini-2.5-flash (Account 2)

Never gives up until all models exhausted.

## Dependencies

- Gemini API credentials configured
- Bash shell

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
