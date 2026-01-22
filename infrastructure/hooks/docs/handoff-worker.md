# handoff-worker.py

Processes queued transcripts into Qdrant.

## What It Does

Background worker that processes the handoff queue. Parses transcripts, summarizes with Gemini, embeds content, and stores to Qdrant's `session_handoffs` collection.

## Event

Background (spawned by `session-end-handoff.py`)

## Pipeline

1. Reads pending entries from `handoff-queue.jsonl`
2. Parses JSONL transcripts into structured data
3. Summarizes with Gemini using structured schema:
   - Key Decisions Made
   - Blockers and Issues
   - Code Artifacts Created/Modified
   - Next Steps
4. Embeds using Ollama (parallel with ThreadPoolExecutor)
5. Stores to Qdrant `session_handoffs` collection
6. Marks entries as processed

## Performance

Uses 32-thread parallel embedding for ~32x throughput on GPU.

## Schema

Stores parent summary + 4 child chunks per session.

## Logs

Output written to `worker.log`

## Dependencies

- `google-generativeai` (Gemini)
- `qdrant-client`
- Ollama (embeddings)
- `concurrent.futures` (parallelism)

## Changelog

- 2026-01-19: Moved from scripts/ to hooks/ (39a41dc)
