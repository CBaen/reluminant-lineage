#!/usr/bin/env python3
"""
extract-json.py - Extract JSON from Gemini's messy output

Handles:
- Markdown code blocks (```json ... ```) - case insensitive
- Variations like ``` json, ```JSON, etc.
- "Loaded cached credentials." prefix
- Extra whitespace/newlines
- Nested JSON objects
- Large outputs (65KB+)

Usage:
  cat gemini_output.txt | python extract-json.py > extracted.json
  python extract-json.py < gemini_output.txt > extracted.json
"""

import sys
import re
import json

def extract_json(text):
    """Extract JSON object from text, handling markdown wrappers."""

    # Remove "Loaded cached credentials." line and other Gemini noise
    lines = text.split('\n')
    cleaned_lines = []
    in_json_block = False

    for line in lines:
        stripped = line.strip().lower()

        # Skip known noise lines
        if 'Loaded cached credentials' in line:
            continue
        if stripped.startswith('warning:') or stripped.startswith('error:'):
            continue

        # Track markdown code blocks (case insensitive, with optional space)
        # Matches: ```json, ``` json, ```JSON, ```Json, etc.
        if re.match(r'^```\s*json\s*$', stripped):
            in_json_block = True
            continue
        if stripped == '```' and in_json_block:
            in_json_block = False
            continue
        # Also handle generic code blocks that might contain JSON
        if stripped == '```' and not in_json_block:
            continue

        cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines).strip()

    # Try to find JSON object by matching braces
    brace_count = 0
    start_idx = None
    end_idx = None

    for i, char in enumerate(text):
        if char == '{':
            if brace_count == 0:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx is not None:
                end_idx = i + 1
                break

    if start_idx is not None and end_idx is not None:
        json_str = text[start_idx:end_idx]
        try:
            parsed = json.loads(json_str)
            return json.dumps(parsed)
        except json.JSONDecodeError as e:
            # Debug: print what we tried to parse
            print(f"JSON parse error: {e}", file=sys.stderr)
            print(f"Attempted to parse: {json_str[:200]}...", file=sys.stderr)

    # Fallback: try to parse the whole cleaned text
    try:
        parsed = json.loads(text)
        return json.dumps(parsed)
    except json.JSONDecodeError:
        pass

    return None

if __name__ == "__main__":
    # Read all input (handles large files)
    try:
        input_text = sys.stdin.read()
    except Exception as e:
        print(json.dumps({"error": f"Failed to read input: {e}"}), file=sys.stderr)
        sys.exit(1)

    if not input_text.strip():
        print(json.dumps({"error": "Empty input received"}), file=sys.stderr)
        sys.exit(1)

    result = extract_json(input_text)

    if result:
        print(result)
    else:
        # Provide diagnostic info
        preview = input_text[:500].replace('\n', '\\n')
        print(json.dumps({
            "error": "Could not extract valid JSON",
            "input_length": len(input_text),
            "input_preview": preview
        }), file=sys.stderr)
        sys.exit(1)
