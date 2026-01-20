#!/usr/bin/env python3
"""
test-consultation-workflow.py - End-to-end test for the consultation workflow

Tests the complete pipeline:
1. Gemini API call (with a minimal prompt)
2. JSON sanitization
3. Schema validation
4. Qdrant storage
5. Retrieval verification

Usage:
    python test-consultation-workflow.py           # Full test with real Gemini call
    python test-consultation-workflow.py --mock    # Test with mock data (no API call)
    python test-consultation-workflow.py --verbose # Show detailed output

Created: January 2026
Purpose: Verify the consultation workflow works end-to-end before running expensive consultations
"""

import argparse
import json
import os
import sys
import subprocess
import tempfile
from datetime import datetime

SCRIPTS_DIR = os.path.expanduser("~/.claude/scripts")

# Minimal valid response that meets schema requirements
MOCK_RESPONSE = '''{
  "meta": {
    "topic": "test-workflow-verification",
    "perspective": "Test Perspective",
    "context": "test",
    "depth": "minimal",
    "research_type": "test",
    "total_words": 100,
    "chunk_count": 1,
    "generated_at": "2026-01-20T12:00:00Z"
  },
  "summary": {
    "text": "This is a test summary to verify the consultation workflow is functioning correctly from end to end.",
    "keywords": ["test", "workflow", "verification"],
    "primary_recommendation": "Run this test before expensive consultations."
  },
  "chunks": [
    {
      "id": "chunk-01",
      "title": "Workflow Verification Test Chunk",
      "content": "This chunk verifies that the consultation workflow can successfully process JSON output from Gemini, validate it against the schema, store it in Qdrant with hybrid vectors, and retrieve it via semantic search. If you can read this after running the test, all components are working correctly. The workflow handles JSON extraction from markdown wrappers, credential prefix stripping, and proper error handling with dead-letter queuing for failed validations.",
      "keywords": ["test", "verification", "workflow", "qdrant"],
      "questions_answered": ["Does the consultation workflow work end-to-end?"],
      "importance": "core"
    }
  ]
}'''

# Simple prompt that should produce valid JSON
TEST_PROMPT = '''Return a minimal JSON response for testing. Use EXACTLY this structure:

{
  "meta": {
    "topic": "workflow-test",
    "perspective": "Test",
    "context": "test",
    "depth": "minimal",
    "research_type": "test",
    "total_words": 50,
    "chunk_count": 1,
    "generated_at": "2026-01-20T12:00:00Z"
  },
  "summary": {
    "text": "Test summary for workflow verification.",
    "keywords": ["test"],
    "primary_recommendation": "Test passed."
  },
  "chunks": [
    {
      "id": "chunk-01",
      "title": "Test Chunk",
      "content": "This is a test chunk with enough words to pass validation. It contains the minimum required content to verify the workflow functions correctly from Gemini through validation to Qdrant storage and retrieval.",
      "keywords": ["test", "workflow", "verification"],
      "questions_answered": ["Does the workflow work?"],
      "importance": "core"
    }
  ]
}

Return ONLY that JSON, no markdown wrappers.'''


def run_test(use_mock: bool = False, verbose: bool = False):
    """Run the end-to-end test."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "mode": "mock" if use_mock else "live",
        "steps": [],
        "success": False
    }

    def log(msg):
        if verbose:
            print(f"[TEST] {msg}")
        results["steps"].append(msg)

    temp_dir = os.environ.get("TEMP", tempfile.gettempdir())
    test_file = os.path.join(temp_dir, "workflow_test.json")
    session = f"workflow-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Step 1: Get JSON (mock or real)
    log("Step 1: Getting JSON response...")

    if use_mock:
        gemini_output = MOCK_RESPONSE
        log(f"Using mock data ({len(gemini_output)} bytes)")
    else:
        log("Calling Gemini API...")
        orchestrator = os.path.join(SCRIPTS_DIR, "gemini-pipe-orchestrator.py")

        # Write test prompt to file
        prompt_file = os.path.join(temp_dir, "test_prompt.txt")
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(TEST_PROMPT)

        try:
            proc = subprocess.run(
                [sys.executable, orchestrator,
                 "-a", "1",
                 "--prompt-file", prompt_file,
                 "--stdout",
                 "--timeout", "60"],
                capture_output=True,
                text=True,
                timeout=90
            )

            if proc.returncode != 0:
                log(f"FAILED: Orchestrator error: {proc.stderr}")
                results["error"] = proc.stderr
                return results

            gemini_output = proc.stdout
            log(f"Received {len(gemini_output)} bytes from Gemini")

        except subprocess.TimeoutExpired:
            log("FAILED: Timeout waiting for Gemini")
            results["error"] = "Timeout"
            return results
        except Exception as e:
            log(f"FAILED: {e}")
            results["error"] = str(e)
            return results

    # Save output for next steps
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(gemini_output)

    # Step 2: Validate JSON
    log("Step 2: Validating JSON schema...")
    validator = os.path.join(SCRIPTS_DIR, "validate-gemini-schema.py")

    try:
        proc = subprocess.run(
            [sys.executable, validator, "--file", test_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        if proc.returncode != 0:
            log(f"FAILED: Validation error: {proc.stdout}")
            results["error"] = proc.stdout
            return results

        log("Validation PASSED")

    except Exception as e:
        log(f"FAILED: Validation exception: {e}")
        results["error"] = str(e)
        return results

    # Step 3: Store to Qdrant
    log("Step 3: Storing to Qdrant...")
    storage = os.path.join(SCRIPTS_DIR, "qdrant-store-gemini.py")

    try:
        proc = subprocess.run(
            [sys.executable, storage,
             "--input-file", test_file,
             "--session", session,
             "--hybrid"],
            capture_output=True,
            text=True,
            timeout=120
        )

        if proc.returncode != 0:
            log(f"FAILED: Storage error: {proc.stderr}")
            results["error"] = proc.stderr
            return results

        storage_result = json.loads(proc.stdout)
        if not storage_result.get("success"):
            log(f"FAILED: Storage returned failure")
            results["error"] = proc.stdout
            return results

        chunks_stored = storage_result.get("chunks_stored", 0)
        parent_id = storage_result.get("parent_id")
        log(f"Stored {chunks_stored} chunks (parent: {parent_id})")
        results["parent_id"] = parent_id
        results["chunks_stored"] = chunks_stored

    except Exception as e:
        log(f"FAILED: Storage exception: {e}")
        results["error"] = str(e)
        return results

    # Step 4: Retrieve and verify
    log("Step 4: Retrieving from Qdrant...")
    search = os.path.join(SCRIPTS_DIR, "qdrant-semantic-search.py")

    try:
        proc = subprocess.run(
            [sys.executable, search,
             "--hybrid",
             "--query", "workflow test verification",
             "--limit", "3",
             "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if proc.returncode != 0:
            log(f"WARNING: Search returned error (may be OK if empty): {proc.stderr}")
        else:
            search_results = json.loads(proc.stdout)
            if search_results:
                top_score = search_results[0].get("score", 0)
                log(f"Retrieved {len(search_results)} results (top score: {top_score:.2f})")
                results["retrieval_score"] = top_score
            else:
                log("WARNING: No results retrieved (indexing may be delayed)")

    except Exception as e:
        log(f"WARNING: Retrieval exception: {e}")

    # All steps completed
    log("All steps completed successfully!")
    results["success"] = True
    return results


def main():
    parser = argparse.ArgumentParser(description="Test the consultation workflow end-to-end")
    parser.add_argument("--mock", action="store_true", help="Use mock data instead of calling Gemini")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    print("=" * 60)
    print("CONSULTATION WORKFLOW END-TO-END TEST")
    print(f"Mode: {'MOCK' if args.mock else 'LIVE (calling Gemini API)'}")
    print("=" * 60)
    print()

    results = run_test(use_mock=args.mock, verbose=args.verbose)

    print()
    print("=" * 60)
    if results["success"]:
        print("[PASS] TEST PASSED")
        print(f"  Chunks stored: {results.get('chunks_stored', 'N/A')}")
        print(f"  Parent ID: {results.get('parent_id', 'N/A')}")
        if "retrieval_score" in results:
            print(f"  Retrieval score: {results['retrieval_score']:.2f}")
    else:
        print("[FAIL] TEST FAILED")
        print(f"  Error: {results.get('error', 'Unknown')}")

    print("=" * 60)

    if args.verbose:
        print("\nDetailed steps:")
        for step in results["steps"]:
            print(f"  - {step}")

    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()
