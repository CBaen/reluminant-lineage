#!/usr/bin/env python3
"""
DEPRECATED - 2026 CONSOLIDATION

Auto-handoff to Qdrant has been disabled in favor of manual HANDOFF.md files.
Rationale: Files provide richer narrative context that doesn't summarize well.

For handoff continuation, read project HANDOFF.md files directly.
For knowledge discovery, query universal_vault collection.

---

Handoff Worker - Processes queued transcripts into Qdrant.

This worker:
1. Reads pending entries from the queue file
2. Parses transcripts using Gemini for intelligent summarization
3. Stores results to Qdrant using existing schema
4. Marks entries as processed

Uses ThreadPoolExecutor for parallel embedding (32x throughput on T600 GPU).
Designed to run asynchronously - spawned by session-end-handoff.py hook.
"""

import json
import sys
import os
import subprocess
import tempfile
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import uuid
import requests

CLAUDE_DIR = Path.home() / ".claude"
QUEUE_FILE = CLAUDE_DIR / "hooks" / "handoff-queue.jsonl"
WORKER_LOG = CLAUDE_DIR / "hooks" / "worker.log"
QDRANT_STORE_SCRIPT = CLAUDE_DIR / "scripts" / "qdrant-store-gemini.py"
GEMINI_SCRIPT = CLAUDE_DIR / "scripts" / "gemini-account.sh"
QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"

# Collection for session handoffs
SESSION_COLLECTION = "session_handoffs"


def log(msg: str):
    """Write to worker log."""
    timestamp = datetime.now().isoformat()
    with open(WORKER_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")


def ensure_collection_exists():
    """Create Qdrant collection if it doesn't exist."""
    try:
        response = requests.get(f"{QDRANT_URL}/collections/{SESSION_COLLECTION}")
        if response.status_code == 404:
            # Create with 768 dimensions for nomic-embed-text
            requests.put(
                f"{QDRANT_URL}/collections/{SESSION_COLLECTION}",
                json={
                    "vectors": {"size": 768, "distance": "Cosine"}
                }
            )
            log(f"Created collection: {SESSION_COLLECTION}")
    except Exception as e:
        log(f"Error checking collection: {e}")


def get_embedding(text: str) -> list:
    """Get embedding from Ollama nomic-embed-text."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=30
        )
        return response.json().get("embedding", [])
    except Exception as e:
        log(f"Embedding error: {e}")
        return []


def parse_transcript(transcript_path: str) -> dict:
    """Parse JSONL transcript into structured data."""
    try:
        messages = []
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Extract text content from messages
        conversation = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if isinstance(content, list):
                # Handle content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                content = " ".join(text_parts)
            if content:
                conversation.append(f"{role}: {content[:500]}")  # Truncate long messages

        return {
            "message_count": len(messages),
            "conversation_preview": "\n".join(conversation[:20]),  # First 20 exchanges
            "full_length": len(conversation)
        }

    except Exception as e:
        log(f"Parse error for {transcript_path}: {e}")
        return {"error": str(e)}


def summarize_with_gemini(transcript_preview: str, session_id: str) -> dict:
    """Use Gemini to create structured summary in our schema."""
    try:
        prompt = f"""DO NOT use any tools. DO NOT wrap output in markdown code blocks.

You are extracting a SESSION HANDOFF from a Claude Code conversation.

CONVERSATION PREVIEW:
{transcript_preview[:8000]}

EXTRACT into this JSON schema:
{{
  "meta": {{
    "topic": "Session summary - main topic worked on",
    "perspective": "session_handoff",
    "context": "session_decisions",
    "research_type": "session_decisions",
    "total_words": 500,
    "chunk_count": 4,
    "generated_at": "{datetime.now().isoformat()}"
  }},
  "summary": {{
    "text": "2-4 sentence session summary: what was worked on, key outcomes",
    "keywords": ["key", "topics", "discussed"]
  }},
  "chunks": [
    {{
      "id": "decisions-01",
      "title": "Key Decisions Made",
      "content": "List decisions made during session with rationale",
      "keywords": ["decisions"],
      "questions_answered": ["What was decided?"],
      "related_chunks": ["blockers-01"],
      "importance": "core"
    }},
    {{
      "id": "blockers-01",
      "title": "Blockers and Issues",
      "content": "Problems encountered, workarounds applied, unresolved issues",
      "keywords": ["blockers", "issues"],
      "questions_answered": ["What problems occurred?"],
      "related_chunks": ["next-01"],
      "importance": "core"
    }},
    {{
      "id": "artifacts-01",
      "title": "Code Artifacts Created/Modified",
      "content": "Files created, functions written, changes made",
      "keywords": ["code", "artifacts"],
      "questions_answered": ["What was built?"],
      "related_chunks": ["decisions-01"],
      "importance": "core"
    }},
    {{
      "id": "next-01",
      "title": "Next Steps",
      "content": "What remains to be done, pending tasks, future work",
      "keywords": ["next", "todo"],
      "questions_answered": ["What comes next?"],
      "related_chunks": [],
      "importance": "core"
    }}
  ]
}}

Return ONLY valid JSON. No markdown. No explanation."""

        # Use Git Bash to run gemini-account.sh (same pattern as gemini-research-store.py)
        git_bash_candidates = [
            r"C:\Program Files\Git\usr\bin\bash.exe",
            r"C:\Program Files\Git\bin\bash.exe",
        ]
        git_bash = None
        for path in git_bash_candidates:
            if os.path.exists(path):
                git_bash = path
                break
        if not git_bash:
            git_bash = "bash"

        gemini_script = CLAUDE_DIR / "scripts" / "gemini-account.sh"

        # Pass prompt directly as argument (subprocess handles escaping)
        result = subprocess.run(
            [git_bash, str(gemini_script), "1", prompt, "gemini-2.0-flash"],
            capture_output=True,
            text=True,
            timeout=120
        )

        output = result.stdout.strip()
        if not output:
            output = result.stderr.strip()

        log(f"Gemini raw output length: {len(output)}")

        # Clean Gemini output (remove credentials message, markdown blocks)
        if "Loaded cached credentials" in output:
            lines = output.split("\n")
            output = "\n".join(lines[1:])

        output = output.strip()

        if output.startswith("```json"):
            output = output[7:]
        elif output.startswith("```"):
            output = output[3:]

        if output.endswith("```"):
            output = output[:-3]

        output = output.strip()

        # Try to find JSON in output
        if not output.startswith("{"):
            # Find first { and last }
            start = output.find("{")
            end = output.rfind("}") + 1
            if start >= 0 and end > start:
                output = output[start:end]

        return json.loads(output)

    except subprocess.TimeoutExpired:
        log("Gemini timeout")
        return None
    except json.JSONDecodeError as e:
        log(f"JSON parse error from Gemini: {e}")
        return None
    except Exception as e:
        log(f"Gemini error: {e}")
        return None


def store_to_qdrant(summary_data: dict, session_id: str):
    """Store summary to Qdrant using our schema."""
    try:
        ensure_collection_exists()

        # Create parent point (summary) - use UUID for Qdrant compatibility
        parent_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"session-{session_id}"))
        summary_text = summary_data.get("summary", {}).get("text", "")

        # Batch embed all chunks using ThreadPoolExecutor (32x speedup)
        chunks = summary_data.get("chunks", [])
        texts_to_embed = [summary_text] + [c.get("content", "") for c in chunks]

        with ThreadPoolExecutor(max_workers=min(len(texts_to_embed), 32)) as executor:
            embeddings = list(executor.map(get_embedding, texts_to_embed))

        if not embeddings[0]:
            log("Failed to get embeddings")
            return False

        # Generate UUIDs for chunks (deterministic based on session + chunk ID)
        chunk_uuids = {
            c["id"]: str(uuid.uuid5(uuid.NAMESPACE_DNS, f"session-{session_id}-{c['id']}"))
            for c in chunks
        }

        # Store summary point
        points = [{
            "id": parent_uuid,
            "vector": embeddings[0],
            "payload": {
                "type": "summary",
                "session_id": session_id,
                **summary_data.get("meta", {}),
                **summary_data.get("summary", {}),
                "child_ids": list(chunk_uuids.values())
            }
        }]

        # Store chunk points
        for i, chunk in enumerate(chunks):
            if embeddings[i + 1]:
                points.append({
                    "id": chunk_uuids[chunk["id"]],
                    "vector": embeddings[i + 1],
                    "payload": {
                        "type": "chunk",
                        "session_id": session_id,
                        "parent_id": parent_uuid,
                        "chunk_id": chunk["id"],
                        "title": chunk.get("title", ""),
                        "text": chunk.get("content", ""),
                        "keywords": chunk.get("keywords", []),
                        "questions_answered": chunk.get("questions_answered", []),
                        "importance": chunk.get("importance", "supporting"),
                        **summary_data.get("meta", {})
                    }
                })

        # Batch upsert to Qdrant
        response = requests.put(
            f"{QDRANT_URL}/collections/{SESSION_COLLECTION}/points",
            json={"points": points},
            params={"wait": "true"}
        )

        if response.status_code == 200:
            log(f"Stored session {session_id[:8]}: {len(points)} points")
            return True
        else:
            log(f"Qdrant error: {response.text}")
            return False

    except Exception as e:
        log(f"Store error: {e}")
        return False


def process_queue():
    """Process all pending entries in the queue."""
    if not QUEUE_FILE.exists():
        return

    try:
        # Read all entries
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return

        processed = []
        remaining = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)

                if entry.get("status") == "processed":
                    continue

                session_id = entry.get("session_id", "unknown")
                transcript_path = entry.get("transcript_path", "")

                log(f"Processing session: {session_id[:8]}")

                # Parse transcript
                parsed = parse_transcript(transcript_path)
                if "error" in parsed:
                    entry["status"] = "error"
                    entry["error"] = parsed["error"]
                    remaining.append(json.dumps(entry))
                    continue

                # Summarize with Gemini
                summary = summarize_with_gemini(
                    parsed.get("conversation_preview", ""),
                    session_id
                )

                if not summary:
                    entry["status"] = "gemini_failed"
                    remaining.append(json.dumps(entry))
                    continue

                # Store to Qdrant
                if store_to_qdrant(summary, session_id):
                    entry["status"] = "processed"
                    entry["processed_at"] = datetime.now().isoformat()
                    processed.append(session_id[:8])
                else:
                    entry["status"] = "store_failed"
                    remaining.append(json.dumps(entry))

            except Exception as e:
                log(f"Entry error: {e}")
                remaining.append(line)

        # Rewrite queue with remaining entries
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            for line in remaining:
                f.write(line + "\n")

        if processed:
            log(f"Completed: {', '.join(processed)}")

    except Exception as e:
        log(f"Queue processing error: {e}")


def main():
    log("Worker started")
    try:
        process_queue()
    except Exception as e:
        log(f"Worker error: {e}")
    log("Worker finished")


if __name__ == "__main__":
    main()
