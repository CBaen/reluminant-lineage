#!/usr/bin/env python3
"""
validate-gemini-schema.py - Strict validation of Gemini JSON output BEFORE storage

PHILOSOPHY: Reject malformed output at the gate, not in the database.

This script validates Gemini's self-chunked research output to ensure:
1. All required fields are present
2. Field types are correct
3. chunk_count matches actual chunk array length
4. Each chunk has required fields
5. Content length is reasonable

Usage:
  # Validate from stdin (pipe mode)
  echo '{"meta": {...}, "chunks": [...]}' | python validate-gemini-schema.py

  # Validate from file
  python validate-gemini-schema.py --file research.json

  # Validate with strict word count
  python validate-gemini-schema.py --file research.json --strict-words

Returns:
  Exit 0 + {"valid": true} on success
  Exit 1 + {"valid": false, "errors": [...]} on failure

Part of the Qdrant 2026 Migration - Schema enforcement layer.
"""

import argparse
import json
import sys
from typing import List, Dict, Any, Tuple


# =============================================================================
# SCHEMA DEFINITIONS
# =============================================================================

REQUIRED_META_FIELDS = {
    "topic": str,
    "chunk_count": int,
    "total_words": int,
    "perspective": str,
    "generated_at": str,
}

OPTIONAL_META_FIELDS = {
    "source": str,
    "session": str,
    "project": str,
    "depth": str,
}

REQUIRED_CHUNK_FIELDS = {
    "id": str,
    "title": str,
    "content": str,
    "keywords": list,
    "questions_answered": list,
    "importance": str,
}

OPTIONAL_CHUNK_FIELDS = {
    "related_chunks": list,
    "word_count": int,
}

VALID_IMPORTANCE_VALUES = {"core", "supporting", "advanced"}

# Content constraints
MIN_CHUNK_WORDS = 50
MAX_CHUNK_WORDS = 800
MIN_KEYWORDS = 3
MIN_QUESTIONS = 1


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def validate_meta(meta: Dict[str, Any]) -> List[str]:
    """Validate meta section of Gemini output."""
    errors = []

    if not isinstance(meta, dict):
        return ["meta must be an object/dictionary"]

    # Check required fields
    for field, expected_type in REQUIRED_META_FIELDS.items():
        if field not in meta:
            errors.append(f"meta.{field} is required but missing")
        elif not isinstance(meta[field], expected_type):
            errors.append(f"meta.{field} must be {expected_type.__name__}, got {type(meta[field]).__name__}")

    # Check chunk_count is positive
    if "chunk_count" in meta and isinstance(meta["chunk_count"], int):
        if meta["chunk_count"] < 1:
            errors.append(f"meta.chunk_count must be >= 1, got {meta['chunk_count']}")

    return errors


def validate_chunk(chunk: Dict[str, Any], index: int) -> List[str]:
    """Validate a single chunk."""
    errors = []
    chunk_id = f"chunk[{index}]"

    if not isinstance(chunk, dict):
        return [f"{chunk_id} must be an object/dictionary"]

    # Check required fields
    for field, expected_type in REQUIRED_CHUNK_FIELDS.items():
        if field not in chunk:
            errors.append(f"{chunk_id}.{field} is required but missing")
        elif not isinstance(chunk[field], expected_type):
            errors.append(f"{chunk_id}.{field} must be {expected_type.__name__}, got {type(chunk[field]).__name__}")

    # Validate importance value
    if "importance" in chunk and isinstance(chunk["importance"], str):
        if chunk["importance"] not in VALID_IMPORTANCE_VALUES:
            errors.append(f"{chunk_id}.importance must be one of {VALID_IMPORTANCE_VALUES}, got '{chunk['importance']}'")

    # Validate content length
    if "content" in chunk and isinstance(chunk["content"], str):
        word_count = count_words(chunk["content"])
        if word_count < MIN_CHUNK_WORDS:
            errors.append(f"{chunk_id}.content too short: {word_count} words (min {MIN_CHUNK_WORDS})")
        if word_count > MAX_CHUNK_WORDS:
            errors.append(f"{chunk_id}.content too long: {word_count} words (max {MAX_CHUNK_WORDS})")

    # Validate keywords array
    if "keywords" in chunk and isinstance(chunk["keywords"], list):
        if len(chunk["keywords"]) < MIN_KEYWORDS:
            errors.append(f"{chunk_id}.keywords has {len(chunk['keywords'])} items (min {MIN_KEYWORDS})")
        # Check keywords are strings
        for i, kw in enumerate(chunk["keywords"]):
            if not isinstance(kw, str):
                errors.append(f"{chunk_id}.keywords[{i}] must be string, got {type(kw).__name__}")

    # Validate questions_answered array
    if "questions_answered" in chunk and isinstance(chunk["questions_answered"], list):
        if len(chunk["questions_answered"]) < MIN_QUESTIONS:
            errors.append(f"{chunk_id}.questions_answered has {len(chunk['questions_answered'])} items (min {MIN_QUESTIONS})")
        # Check questions are strings
        for i, q in enumerate(chunk["questions_answered"]):
            if not isinstance(q, str):
                errors.append(f"{chunk_id}.questions_answered[{i}] must be string, got {type(q).__name__}")

    return errors


def validate_gemini_output(data: Dict[str, Any], strict_words: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate complete Gemini research output.

    Args:
        data: Parsed JSON from Gemini
        strict_words: If True, also validate total_words accuracy

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check top-level structure
    if not isinstance(data, dict):
        return False, ["Root must be an object/dictionary"]

    if "meta" not in data:
        errors.append("'meta' section is required but missing")
    if "chunks" not in data:
        errors.append("'chunks' section is required but missing")

    if errors:
        return False, errors

    # Validate meta
    meta_errors = validate_meta(data["meta"])
    errors.extend(meta_errors)

    # Validate chunks array
    chunks = data.get("chunks", [])
    if not isinstance(chunks, list):
        errors.append("'chunks' must be an array")
        return False, errors

    if len(chunks) == 0:
        errors.append("'chunks' array is empty (must have at least 1 chunk)")

    # Check chunk_count matches array length
    meta = data.get("meta", {})
    if "chunk_count" in meta and isinstance(meta["chunk_count"], int):
        if meta["chunk_count"] != len(chunks):
            errors.append(f"meta.chunk_count ({meta['chunk_count']}) does not match actual chunk count ({len(chunks)})")

    # Validate each chunk
    for i, chunk in enumerate(chunks):
        chunk_errors = validate_chunk(chunk, i)
        errors.extend(chunk_errors)

    # Validate total_words accuracy (if strict mode)
    if strict_words and "total_words" in meta:
        actual_words = sum(
            count_words(c.get("content", ""))
            for c in chunks
            if isinstance(c, dict)
        )
        reported_words = meta.get("total_words", 0)
        # Allow 10% tolerance
        tolerance = max(50, int(actual_words * 0.1))
        if abs(actual_words - reported_words) > tolerance:
            errors.append(f"meta.total_words ({reported_words}) differs from actual ({actual_words}) by more than {tolerance}")

    return len(errors) == 0, errors


def validate_summary_output(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate summary-style output (no chunks, just summary text).
    Used for simpler research outputs.
    """
    errors = []

    if not isinstance(data, dict):
        return False, ["Root must be an object/dictionary"]

    required = ["topic", "summary"]
    for field in required:
        if field not in data:
            errors.append(f"'{field}' is required but missing")

    if "summary" in data:
        if not isinstance(data["summary"], str):
            errors.append("'summary' must be a string")
        elif count_words(data["summary"]) < 50:
            errors.append("'summary' too short (min 50 words)")

    return len(errors) == 0, errors


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Validate Gemini JSON output against 2026 schema",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--file", "-f", help="JSON file to validate (or use stdin)")
    parser.add_argument("--strict-words", action="store_true",
                        help="Strictly validate total_words accuracy")
    parser.add_argument("--summary-mode", action="store_true",
                        help="Validate as summary output (no chunks)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Only output valid/invalid, no error details")

    args = parser.parse_args()

    # Read input
    try:
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        result = {"valid": False, "errors": [f"Invalid JSON: {e}"]}
        print(json.dumps(result))
        sys.exit(1)
    except Exception as e:
        result = {"valid": False, "errors": [f"Error reading input: {e}"]}
        print(json.dumps(result))
        sys.exit(1)

    # Validate
    if args.summary_mode:
        is_valid, errors = validate_summary_output(data)
    else:
        is_valid, errors = validate_gemini_output(data, strict_words=args.strict_words)

    # Output result
    if args.quiet:
        result = {"valid": is_valid}
    else:
        result = {"valid": is_valid}
        if not is_valid:
            result["errors"] = errors
            result["error_count"] = len(errors)

    print(json.dumps(result, indent=2))
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
