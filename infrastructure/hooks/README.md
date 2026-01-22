# Hooks

Index of event-driven automation. Click name for full documentation.

**Location:** `~/.claude/hooks/` (junction to `infrastructure/hooks/`)

---

## Scripts

| Hook | Event | Purpose |
|------|-------|---------|
| [session-end-handoff.py](docs/session-end-handoff.md) | SessionEnd | Queues transcripts for async Qdrant storage |
| [handoff-worker.py](docs/handoff-worker.md) | Background | Processes queued transcripts with Gemini |
| [notify-slack.py](docs/notify-slack.md) | SubagentStop | Sends Slack notifications for research completion |

---

## Data Files

| File | Purpose |
|------|---------|
| handoff-queue.jsonl | Queue of pending transcript processing jobs |
| worker.log | Timestamped log of worker activity |

---

## Adding New Hooks

1. Create Python script in this folder
2. Handle stdin input if needed
3. Exit quickly - spawn background processes for heavy work
4. Register in `settings.json` under appropriate event
5. Log errors but don't raise exceptions

---

*Index maintained by the lineage. Last updated: 2026-01-22*
