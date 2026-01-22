# validate-gemini-schema.py

Validate Gemini JSON before storage.

## What It Does

Validates that Gemini's JSON output conforms to the expected research schema before storing to Qdrant. Catches malformed responses early.

## Usage

```bash
# From stdin
echo '{"meta":...}' | python validate-gemini-schema.py

# From file
python validate-gemini-schema.py --file research.json

# Strict word count validation
python validate-gemini-schema.py --file research.json --strict-words
```

## Options

| Option | Description |
|--------|-------------|
| `--file` | Input file path |
| `--strict-words` | Enforce word count limits |

## Validation Checks

- Required fields present
- Correct data types
- Chunk structure valid
- Word counts within limits (if strict)

## Output

- Exit 0 + `{"valid": true}` on success
- Exit 1 + `{"valid": false, "errors": [...]}` on failure

## Dependencies

- None (pure Python)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
