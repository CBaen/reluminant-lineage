# Hooks Reference

Event-driven automation that fires on Claude Code lifecycle events.

**Location:** `~/.claude/hooks/` (junction to `infrastructure/hooks/`)

---

## Overview

Hooks are Python scripts triggered by Claude Code events. They run asynchronously to avoid blocking the CLI.

**Configuration:** Hooks are registered in `settings.json` under the appropriate event type.

---

## Session Handoff System

Two scripts work together to index session transcripts into Qdrant:

### session-end-handoff.py

**Event:** SessionEnd
**Purpose:** Queues transcripts for async processing

**What it does:**
1. Receives `{session_id, transcript_path}` from stdin when session ends
2. Writes entry to queue file (`handoff-queue.jsonl`)
3. Spawns worker asynchronously
4. Exits immediately (doesn't block CLI)

**Configuration in settings.json:**
```json
{
  "hooks": {
    "SessionEnd": [{
      "type": "command",
      "command": "python C:/Users/baenb/.claude/hooks/session-end-handoff.py"
    }]
  }
}
```

**Input:** JSON on stdin
```json
{
  "session_id": "abc123",
  "transcript_path": "C:/Users/baenb/.claude/projects/.../transcript.jsonl"
}
```

---

### handoff-worker.py

**Event:** Background (spawned by session-end-handoff.py)
**Purpose:** Processes queued transcripts into Qdrant

**Pipeline:**
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

**Performance:** Uses 32-thread parallel embedding for ~32x throughput on GPU.

**Logs:** Output written to `worker.log`

**Schema:** Stores parent summary + 4 child chunks per session.

---

## Slack Notifications

### notify-slack.py

**Event:** SubagentStop
**Purpose:** Sends rich Slack notifications when research tasks complete

**Triggers on subagent types:**
- gemini-researcher
- lineage-research
- lineage-consult
- Explore
- feature-dev:code-architect
- feature-dev:code-explorer
- decision-weigher
- research-analyst

**Configuration:**
```bash
# Option 1: Environment variable
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# Option 2: Config file
# Create ~/.claude/config/notifications.json
{
  "enabled": true,
  "webhook_url": "https://hooks.slack.com/services/...",
  "notify_on_types": ["gemini-researcher", "lineage-research"],
  "include_result_preview": true,
  "max_preview_length": 500
}
```

**Message format:** Rich Slack blocks with:
- Header with emoji based on agent type
- Timestamp
- Result preview (truncated)
- Action hint for retrieval

---

## Data Files

### handoff-queue.jsonl

Queue of pending transcript processing jobs.

**Format:** One JSON object per line
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "queued_at": "2026-01-22T10:30:00",
  "status": "pending"
}
```

**Status values:**
- `pending` - Awaiting processing
- `processed` - Successfully stored to Qdrant
- `error` - Parse error (see `error` field)
- `gemini_failed` - Gemini summarization failed
- `store_failed` - Qdrant storage failed

---

### worker.log

Timestamped log of worker activity.

**Format:**
```
[2026-01-22T10:30:00] Worker started
[2026-01-22T10:30:01] Processing session: abc123
[2026-01-22T10:30:15] Stored session abc123: 5 points
[2026-01-22T10:30:15] Worker finished
```

Use to debug handoff issues or monitor processing.

---

## Adding New Hooks

1. Create Python script in this folder
2. Handle stdin input if needed (Claude Code passes context)
3. Exit quickly - spawn background processes for heavy work
4. Register in `settings.json` under appropriate event
5. Log errors but don't raise exceptions (avoid blocking CLI)

**Available events:** See Claude Code documentation for full list.

---

*Maintained by the lineage. Last updated: 2026-01-22*
