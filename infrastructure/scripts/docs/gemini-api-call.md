# gemini-api-call.py

Direct Gemini API calls with proper timeout handling.

## What It Does

Makes direct calls to Gemini API using the google-generativeai SDK. Handles timeouts, retries, and error reporting without agentic CLI overhead.

## Usage

```bash
# Direct prompt
python gemini-api-call.py --account 1 --prompt "Your prompt"

# From file
python gemini-api-call.py --account 1 --prompt-file prompt.txt

# Specific model
python gemini-api-call.py --account 1 --prompt "query" --model gemini-2.5-flash
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--account` | Account number (1 or 2) | Required |
| `--prompt` | Direct prompt text | - |
| `--prompt-file` | File containing prompt | - |
| `--model` | Model to use | gemini-2.5-pro |
| `--timeout` | Request timeout in seconds | 120 |

## Dependencies

- `google-generativeai` SDK
- Gemini API credentials

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
