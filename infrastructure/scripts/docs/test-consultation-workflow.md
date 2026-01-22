# test-consultation-workflow.py

Test the consultation workflow end-to-end.

## What It Does

Runs a test consultation to verify the entire workflow is functioning: prompt creation, Gemini call, validation, and Qdrant storage.

## Usage

```bash
python test-consultation-workflow.py
```

## What It Tests

1. Prompt builder generates valid prompt
2. Gemini API responds
3. Response validates against schema
4. Qdrant storage succeeds
5. Retrieval returns stored content

## Output

Pass/fail status for each step with error details if any fail.

## Dependencies

- All consultation workflow components
- Gemini API credentials
- Qdrant running

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
