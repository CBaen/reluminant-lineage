# extract-json.py

Extract JSON from Gemini's messy output.

## What It Does

Cleans and extracts valid JSON from Gemini responses that may contain markdown formatting, explanatory text, or other non-JSON content.

## Usage

```bash
cat output.txt | python extract-json.py > clean.json
```

## Handles

- Markdown code blocks (```json ... ```)
- Text prefixes ("Here's the JSON:")
- Trailing explanations after JSON
- Nested JSON objects
- Large outputs (65KB+)
- Multiple JSON objects (returns first valid)

## Output

Clean JSON to stdout. Exits with error if no valid JSON found.

## Dependencies

- None (pure Python)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
