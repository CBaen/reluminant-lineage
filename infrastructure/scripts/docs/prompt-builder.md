# prompt-builder.py

Generate optimized LLM prompts.

## What It Does

Builds structured prompts for Gemini research queries using templates optimized for different research types.

## Usage

```bash
# Default technical template
python prompt-builder.py 'topic' 'context' | gemini

# Historical research template
python prompt-builder.py 'topic' 'context' --type historical

# Comparative analysis
python prompt-builder.py 'topic' 'context' --type comparative
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--type` | Template type | technical |

## Templates

| Type | Purpose |
|------|---------|
| technical | Technical documentation and how-to |
| historical | Historical context and evolution |
| comparative | Compare alternatives and trade-offs |

## Output

Formatted prompt string to stdout.

## Dependencies

- None (pure Python)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
