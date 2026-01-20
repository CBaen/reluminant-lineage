#!/usr/bin/env python3
"""
gemini-json-helper.py - Standard patterns for getting reliable JSON from Gemini

CRITICAL FINDING: Gemini 2.0 Flash does NOT have JSON mode.
You MUST use explicit prompting patterns.

Usage:
    from gemini_json_helper import wrap_prompt_for_json, clean_json_response

Or standalone:
    python gemini-json-helper.py wrap "Your prompt" '{"schema": "here"}'
    python gemini-json-helper.py clean "```json\n{...}\n```"
"""

import sys
import re
import json

# ==============================================================================
# PROMPT PATTERNS FOR RELIABLE JSON OUTPUT
# ==============================================================================

JSON_INSTRUCTION_BLOCK = """
CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY valid JSON
- Do NOT wrap in markdown code blocks (no ```)
- Do NOT include any text before or after the JSON
- Do NOT include explanations, notes, or commentary
- The response must start with { and end with }
"""

def wrap_prompt_for_json(prompt: str, schema: dict = None, example: dict = None) -> str:
    """
    Wrap a prompt with explicit JSON output instructions.

    Args:
        prompt: The main task/question prompt
        schema: Optional JSON schema showing expected structure
        example: Optional example output

    Returns:
        Enhanced prompt with JSON requirements
    """
    parts = [prompt, "", JSON_INSTRUCTION_BLOCK]

    if schema:
        parts.append("\nEXPECTED JSON SCHEMA:")
        parts.append(json.dumps(schema, indent=2))

    if example:
        parts.append("\nEXAMPLE OUTPUT (follow this format exactly):")
        parts.append(json.dumps(example, indent=2))

    parts.append("\nRemember: Output ONLY the JSON object. Nothing else.")

    return "\n".join(parts)


# ==============================================================================
# RESPONSE CLEANING FOR GEMINI OUTPUT
# ==============================================================================

def clean_json_response(text: str) -> str:
    """
    Clean Gemini's response to extract valid JSON.

    Handles:
    - "Loaded cached credentials." prefix
    - Markdown code block wrappers
    - Leading/trailing whitespace and text
    - Nested braces

    Args:
        text: Raw Gemini response

    Returns:
        Cleaned JSON string
    """
    if not text:
        return ""

    lines = text.strip().split('\n')
    cleaned = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Skip known noise
        if 'Loaded cached credentials' in line:
            continue
        if stripped.startswith('Error executing tool'):
            continue

        # Handle markdown code blocks
        if re.match(r'^```\s*(json)?\s*$', stripped, re.IGNORECASE):
            in_code_block = not in_code_block
            continue

        cleaned.append(line)

    result = '\n'.join(cleaned).strip()

    # Find complete JSON object by brace matching
    brace_count = 0
    start_idx = None

    for i, char in enumerate(result):
        if char == '{':
            if brace_count == 0:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx is not None:
                return result[start_idx:i+1]

    # If no complete JSON found, return cleaned result
    return result


def parse_json_response(text: str) -> dict:
    """
    Clean and parse Gemini response to JSON.

    Args:
        text: Raw Gemini response

    Returns:
        Parsed JSON dict

    Raises:
        json.JSONDecodeError if parsing fails
    """
    cleaned = clean_json_response(text)
    return json.loads(cleaned)


# ==============================================================================
# STANDARD RESEARCH OUTPUT SCHEMA
# ==============================================================================

RESEARCH_SCHEMA = {
    "meta": {
        "topic": "string",
        "perspective": "string",
        "context": "general|project-specific",
        "depth": "overview|comprehensive|exhaustive",
        "research_type": "knowledge_retrieval|consultation",
        "total_words": "integer",
        "chunk_count": "integer",
        "generated_at": "ISO timestamp"
    },
    "summary": {
        "text": "2-4 sentence overview",
        "keywords": ["array", "of", "keywords"]
    },
    "chunks": [{
        "id": "chunk-01",
        "title": "Clear Searchable Title",
        "content": "200-400 words explaining ONE concept",
        "keywords": ["specific", "to", "chunk"],
        "questions_answered": ["What question does this answer?"],
        "related_chunks": ["chunk-02"],
        "importance": "core|supporting|advanced"
    }]
}

RESEARCH_EXAMPLE = {
    "meta": {
        "topic": "WebSocket Protocol",
        "perspective": "technical-overview",
        "context": "general",
        "depth": "comprehensive",
        "research_type": "knowledge_retrieval",
        "total_words": 2400,
        "chunk_count": 6,
        "generated_at": "2026-01-16T10:30:00Z"
    },
    "summary": {
        "text": "WebSocket is a communication protocol providing full-duplex channels over a single TCP connection. It enables real-time bidirectional data exchange between client and server.",
        "keywords": ["websocket", "real-time", "bidirectional", "tcp", "protocol"]
    },
    "chunks": [{
        "id": "chunk-01",
        "title": "WebSocket Protocol Basics",
        "content": "WebSocket is a computer communications protocol...",
        "keywords": ["protocol", "tcp", "connection"],
        "questions_answered": ["What is WebSocket?"],
        "related_chunks": ["chunk-02"],
        "importance": "core"
    }]
}


# ==============================================================================
# CLI INTERFACE
# ==============================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python gemini-json-helper.py wrap 'prompt' [schema_json]")
        print("  python gemini-json-helper.py clean 'raw_response'")
        print("  python gemini-json-helper.py research-schema")
        sys.exit(1)

    command = sys.argv[1]

    if command == "wrap":
        prompt = sys.argv[2] if len(sys.argv) > 2 else ""
        schema = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
        print(wrap_prompt_for_json(prompt, schema))

    elif command == "clean":
        text = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        print(clean_json_response(text))

    elif command == "research-schema":
        print("SCHEMA:")
        print(json.dumps(RESEARCH_SCHEMA, indent=2))
        print("\nEXAMPLE:")
        print(json.dumps(RESEARCH_EXAMPLE, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
