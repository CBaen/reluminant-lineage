# run-consultation-angle.py

Execute single consultation perspective.

## What It Does

Runs a complete consultation workflow for one perspective: creates prompt, calls Gemini, validates response, and stores to Qdrant. Used by swarm workers for multi-angle consultations.

## Usage

```bash
python run-consultation-angle.py \
  --topic "topic" \
  --context "project context" \
  --perspective "Problem Analysis" \
  --account 1 \
  --session "session-id"
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--topic` | Consultation topic | Required |
| `--context` | Project context | Required |
| `--perspective` | Angle (Problem Analysis, Solution Design, etc.) | Required |
| `--account` | Gemini account | 1 |
| `--session` | Session identifier | Required |

## Perspectives

Common angles:
- Problem Analysis
- Solution Design
- Risk Assessment
- Implementation Strategy
- Alternative Approaches

## Workflow

1. Build consultation prompt with perspective
2. Call Gemini API
3. Validate JSON response
4. Store to Qdrant with perspective metadata

## Dependencies

- `google-generativeai`
- `qdrant-client`

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
