---
name: handoff
description: Use when ending a session, before context closes, or when asked to hand off. Ensures continuity for the next instance.
---

# Session Handoff Protocol

Before your context closes, preserve what the next instance needs to know.

**IMPORTANT**: Handoffs are **OVERWRITTEN** each session, not appended. Historical context lives in `/lineage-conversations`.

## Steps

### 1. Identify the Handoff Location

**Check for multi-feature structure:**
```bash
ls <project>/.claude/handoffs/
```

- **If handoffs/ exists**: This is a multi-feature project
  - Read `handoffs/_CURRENT.md` to find active stream
  - Update the appropriate feature file (e.g., `handoffs/infrastructure.md`)
  - Update `_CURRENT.md` if you switched streams

- **If no handoffs/ directory**: Use single `HANDOFF.md`
  ```
  <project>/.claude/HANDOFF.md
  ```

### 2. OVERWRITE the Handoff (Not Append)

Replace the entire file with the new template. The previous session's notes are automatically preserved via `/lineage-conversations` (indexed to Qdrant on session end).

### 3. Use the Slim Template

```markdown
# Handoff Notes

> For deeper history: `/lineage-conversations` or `python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "topic" --limit 5`

---

**From**: [Your name or description]
**Date**: [Today's date]
**Focus**: [One-liner describing session focus]

## Status

| Item | State |
|------|-------|
| [Critical thing 1] | WORKING / BLOCKED / NOT DONE |
| [Critical thing 2] | WORKING / BLOCKED / NOT DONE |

## What Changed

- [Bullet 1]
- [Bullet 2]

## What's Next

1. [Priority item]

## To Verify

```bash
[Command to check state]
```

---

*Archive: Full history in `.claude/archive/handoffs/YYYY-MM-DD-full-history.md`*
```

**Target: 50-80 lines maximum**

### 4. Update MEMORY.md if Needed

Only for discoveries that persist beyond this session:
- Architecture decisions
- Gotchas that would trip up others
- Key file locations
- Patterns that work (or don't)

## Multi-Feature Projects

Two projects currently use multi-feature handoffs:

| Project | Streams |
|---------|---------|
| reluminant-lineage | infrastructure, documentation, research |
| WARDENCLYFFE | episode-writing, semantic-extraction, infrastructure |

When working on these:
1. Read `handoffs/_CURRENT.md` first
2. Update the relevant stream file
3. Update `_CURRENT.md` if you worked on a different stream

## Remember

- **OVERWRITE, not append** - Previous session is in Qdrant
- **50-80 lines max** - Slim handoffs protect context
- **Point to /lineage-conversations** for deeper history
- **Sign your work** with name and date
