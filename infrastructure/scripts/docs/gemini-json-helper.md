# gemini-json-helper.py

Reliable JSON extraction from Gemini output.

## What It Does

Wraps prompts for JSON output and cleans Gemini responses to extract valid JSON. Critical because Gemini 2.0 Flash does NOT have a native JSON mode.

## Usage

### As Module

```python
from gemini_json_helper import wrap_prompt_for_json, clean_json_response

# Wrap prompt to request JSON
wrapped = wrap_prompt_for_json(prompt, schema)

# Clean response
clean = clean_json_response(response)
```

### As CLI

```bash
# Wrap a prompt
python gemini-json-helper.py wrap "Your prompt" '{"schema": "here"}'

# Clean a response
python gemini-json-helper.py clean "```json\n{...}\n```"
```

## Cleaning Handles

- Markdown code blocks (```json)
- Text prefixes ("Here's the JSON:")
- Trailing text after JSON
- Nested objects
- Large outputs (65KB+)

## Dependencies

- None (pure Python)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
