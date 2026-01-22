# gemini-parallel.sh

Execute multiple Gemini queries in parallel.

## What It Does

Runs multiple Gemini queries concurrently, collecting results. Each result is stored to Qdrant automatically.

## Usage

```bash
# Direct prompts
~/.claude/scripts/gemini-parallel.sh "prompt1" "prompt2" "prompt3"

# From file (one prompt per line)
~/.claude/scripts/gemini-parallel.sh --file prompts.txt
```

## Arguments

| Argument | Description |
|----------|-------------|
| `"prompt"` | Individual prompts as arguments |
| `--file` | File with prompts (one per line) |

## Behavior

- Uses single account for all queries
- Results stored with session identifier
- Failures logged but don't stop other queries

## Dependencies

- Bash shell
- Gemini API credentials

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
