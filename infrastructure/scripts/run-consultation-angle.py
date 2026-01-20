#!/usr/bin/env python3
"""
run-consultation-angle.py - Execute a single consultation angle

This script handles the complete workflow for one consultation perspective:
1. Creates the prompt file with proper date injection
2. Calls Gemini via the orchestrator
3. Validates the output
4. Stores to Qdrant

Designed to be called by the consultation-swarm-worker agent without
requiring bash heredocs (which fail in PowerShell on Windows).

Usage:
    python run-consultation-angle.py \
        --topic "Your topic" \
        --context "Project context..." \
        --perspective "Problem Analysis" \
        --account 1 \
        --session "my-session" \
        --collection "universal_vault" \
        --angle-num 1

Returns JSON with success/failure status and details.
"""

import argparse
import json
import os
import sys
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


PROMPT_TEMPLATE = '''TODAY: {date}. Search Google for current information dated 2025-2026.

You are producing a DOCTORAL THESIS on this topic. Your output will be stored in a vector database for long-term retrieval. Treat this as permanent knowledge infrastructure.

== CONSULTATION REQUEST ==

TOPIC: {topic}
PERSPECTIVE: {perspective}

CLIENT CONTEXT (your recommendations MUST reference specifics from this):
{context}

== YOUR MISSION ==

Write the DOCTORAL DISSERTATION on this topic from the specified perspective.

This is not a summary. This is not an overview. This is the COMPLETE REFERENCE BOOK - the kind that sits on a shelf and gets consulted for years. A senior engineer should be able to open this and find EVERYTHING they need to understand and implement this topic for THIS CLIENT'S specific context.

USE YOUR FULL CAPABILITIES:
- Search Google for current information (2025-2026)
- CITE YOUR SOURCES with URLs where possible
- Include specific version numbers, documentation links, and references
- If you reference a technique, library, or approach - link to where someone can learn more

COVERAGE REQUIREMENTS - address ALL of these dimensions:
- Core concepts: What must be understood first?
- Theory and rationale: WHY do things work this way?
- Practical implementation: HOW to actually do it in this stack?
- Edge cases: What breaks? What's weird? What's unexpected?
- Limitations: What CAN'T this approach do?
- Common mistakes: What do people get wrong?
- Best practices: What do experts do differently?
- Integration points: How does this connect to other systems?
- Performance considerations: What affects speed, memory, reliability?
- Security implications: What could go wrong? How to protect against it?
- Future considerations: What might change? What should we watch?

QUALITY STANDARD:
- Every recommendation MUST reference something specific in the client context
- If a recommendation could apply to anyone, it's too generic - make it specific or remove it
- Include code examples, configuration snippets, or specific commands where relevant
- Explain the WHY behind every recommendation, not just the WHAT

== OUTPUT FORMAT ==

Return ONLY valid JSON. No markdown wrappers. No explanations before or after.

{{
  "meta": {{
    "topic": "{topic}",
    "perspective": "{perspective}",
    "context": "project-specific",
    "project_context_summary": "One sentence summary of client context",
    "depth": "exhaustive",
    "research_type": "expert_consultation",
    "total_words": 5000,
    "chunk_count": 12,
    "generated_at": "{timestamp}"
  }},
  "summary": {{
    "text": "Executive summary of this perspective's findings (100+ words)",
    "keywords": ["relevant", "domain", "keywords"],
    "primary_recommendation": "The single most important action to take"
  }},
  "chunks": [
    {{
      "id": "chunk-01",
      "title": "Clear descriptive title for this section",
      "content": "50-800 words of substantive content. This is where your expertise goes. Explain thoroughly. Include specifics. Reference the client context. Provide actionable guidance.",
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "questions_answered": ["What question does this chunk answer?"],
      "importance": "core",
      "action_items": ["Specific action the client should take"],
      "sources": ["https://docs.example.com/relevant-page", "Library documentation v2.3"]
    }}
  ],
  "implementation_plan": {{
    "phases": [
      {{
        "phase": 1,
        "title": "Phase name",
        "description": "What this phase accomplishes",
        "tasks": [
          {{"order": 1, "task": "Specific task", "rationale": "Why this matters", "status": "pending"}}
        ]
      }}
    ],
    "critical_decisions": ["Decisions that must be made"],
    "risks": ["What could go wrong"],
    "success_criteria": ["How to know when done"]
  }}
}}

NOTE: chunk_count in meta MUST EXACTLY equal the number of items in your chunks array.
If you have 15 chunks, chunk_count must be 15. Validation will FAIL if they don't match.

CHUNK REQUIREMENTS (for Qdrant storage compatibility):
- "id": unique identifier like "chunk-01", "chunk-02", etc.
- "title": clear section title (required)
- "content": 50-800 words per chunk (required) - if you have more to say, create more chunks
- "keywords": at least 3 relevant terms (required)
- "questions_answered": at least 1 question this chunk answers (required)
- "importance": exactly one of "core", "supporting", or "advanced" (required)
- "action_items": specific actions for this client (optional but valuable)
- "sources": URLs, documentation links, or citations supporting this chunk (optional but valuable)

Create as many chunks as needed to fully cover the topic. Complex topics might need 20-30+ chunks.
Let the content determine the structure, not arbitrary limits. This is a reference book, not a blog post.

Return ONLY JSON.
'''


def run_angle(topic: str, context: str, perspective: str, account: int,
              session: str, collection: str, angle_num: int, timeout: int = 600) -> dict:
    """Execute a single consultation angle."""

    scripts_dir = os.path.expanduser("~/.claude/scripts")
    temp_dir = os.environ.get("TEMP", "/tmp")

    result = {
        "angle_num": angle_num,
        "perspective": perspective,
        "account": account,
        "success": False,
        "gemini_bytes": 0,
        "chunks_stored": 0,
        "validation_passed": False,
        "error": None
    }

    # Step 1: Create prompt file
    prompt = PROMPT_TEMPLATE.format(
        date=datetime.now().strftime("%Y-%m-%d"),
        topic=topic,
        perspective=perspective,
        context=context,
        timestamp=datetime.now().isoformat() + "Z"
    )

    prompt_file = os.path.join(temp_dir, f"prompt_angle_{angle_num}.txt")
    output_file = os.path.join(temp_dir, f"angle_{angle_num}_output.json")

    try:
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"[ANGLE {angle_num}] Wrote prompt ({len(prompt)} chars)", file=sys.stderr)
    except Exception as e:
        result["error"] = f"Failed to write prompt file: {e}"
        return result

    # Step 2: Call Gemini via orchestrator
    orchestrator = os.path.join(scripts_dir, "gemini-pipe-orchestrator.py")
    try:
        proc = subprocess.run(
            [sys.executable, orchestrator,
             "-a", str(account),
             "--prompt-file", prompt_file,
             "--stdout",
             "--timeout", str(timeout)],
            capture_output=True,
            text=True,
            timeout=timeout + 30
        )

        if proc.returncode != 0:
            result["error"] = f"Orchestrator failed: {proc.stderr}"
            return result

        gemini_output = proc.stdout
        result["gemini_bytes"] = len(gemini_output)
        print(f"[ANGLE {angle_num}] Received {len(gemini_output)} bytes from Gemini", file=sys.stderr)

        # Save output for debugging/storage
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(gemini_output)

    except subprocess.TimeoutExpired:
        result["error"] = f"Timeout after {timeout}s"
        return result
    except Exception as e:
        result["error"] = f"Gemini call failed: {e}"
        return result

    # Step 3: Validate output
    validator = os.path.join(scripts_dir, "validate-gemini-schema.py")
    try:
        proc = subprocess.run(
            [sys.executable, validator, "--file", output_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        if proc.returncode != 0:
            result["error"] = f"Validation failed: {proc.stdout or proc.stderr}"
            # Don't return yet - still save to dead letter via orchestrator's mechanism
            return result

        result["validation_passed"] = True
        print(f"[ANGLE {angle_num}] Validation PASSED", file=sys.stderr)

    except Exception as e:
        result["error"] = f"Validation error: {e}"
        return result

    # Step 4: Store to Qdrant
    storage = os.path.join(scripts_dir, "qdrant-store-gemini.py")
    try:
        proc = subprocess.run(
            [sys.executable, storage,
             "--input-file", output_file,
             "--session", session,
             "--hybrid"],  # --hybrid ignores --collection and uses universal_vault
            capture_output=True,
            text=True,
            timeout=120
        )

        if proc.returncode != 0:
            result["error"] = f"Storage failed: {proc.stderr}"
            return result

        try:
            storage_result = json.loads(proc.stdout)
            if storage_result.get("success"):
                result["success"] = True
                result["chunks_stored"] = storage_result.get("chunks_stored", 0)
                result["parent_id"] = storage_result.get("parent_id")
                print(f"[ANGLE {angle_num}] Stored {result['chunks_stored']} chunks", file=sys.stderr)
            else:
                result["error"] = f"Storage returned failure: {proc.stdout}"
        except json.JSONDecodeError:
            result["error"] = f"Invalid storage response: {proc.stdout}"

    except Exception as e:
        result["error"] = f"Storage error: {e}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Run a single consultation angle")
    parser.add_argument("--topic", required=True, help="Consultation topic")
    parser.add_argument("--context", required=True, help="Project context")
    parser.add_argument("--perspective", required=True, help="Perspective name")
    parser.add_argument("--account", type=int, choices=[1, 2], required=True)
    parser.add_argument("--session", required=True, help="Session name")
    parser.add_argument("--collection", default="universal_vault", help="Qdrant collection")
    parser.add_argument("--angle-num", type=int, default=1, help="Angle number (1-5)")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")
    parser.add_argument("--context-file", help="Read context from file instead of --context")

    args = parser.parse_args()

    # Allow reading context from file (for very long contexts)
    context = args.context
    if args.context_file:
        with open(args.context_file, 'r', encoding='utf-8') as f:
            context = f.read()

    result = run_angle(
        topic=args.topic,
        context=context,
        perspective=args.perspective,
        account=args.account,
        session=args.session,
        collection=args.collection,
        angle_num=args.angle_num,
        timeout=args.timeout
    )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
