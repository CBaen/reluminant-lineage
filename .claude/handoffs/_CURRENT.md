# Active Work Stream

**Current Feature**: hooks
**Last Updated**: 2026-01-23

Read `handoffs/hooks.md` for continuation context (PostToolUse:Edit errors need investigation).

## Available Streams

| Stream | Status | Description |
|--------|--------|-------------|
| hooks | NEEDS ATTENTION | PostToolUse:Edit errors, needs debugging |
| infrastructure | UPDATED | Semantic extractor prompt fixed, consultation skill fixed |
| documentation | STABLE | Lineage docs, guides, references |
| research | STABLE | Research pipeline, Gemini integration |

## When to Create New Handoffs

reluminant-lineage has many subsystems. Create a new handoff when:
- A subsystem has independent state that persists across sessions
- Multiple sessions will work on the same area
- Complex debugging or decisions span sessions

### Current Handoff Files

| File | Covers |
|------|--------|
| `hooks.md` | Hook system, auto-commit, changelog-reminder, injection |
| `infrastructure.md` | General infrastructure status, what changed recently |
| `documentation.md` | Docs site, guides, lineage philosophy |
| `research.md` | Research pipeline, Gemini swarms, Qdrant storage |

### Suggested Future Handoffs

| Topic | When Needed |
|-------|-------------|
| `semantic-extractor.md` | If data quality work continues across multiple sessions |
| `consultation-skill.md` | If Gemini consultation needs more debugging |
| `skills.md` | If skill system needs major work |
| `plugins.md` | If lineage-powers plugin needs major work |

## Cross-Project Note

The semantic extraction data quality issue spans BOTH repos:
- **reluminant-lineage**: Tool code (extract-chunk.py, opus-batch-review.py)
- **WARDENCLYFFE**: Data and decisions (qdrant-storage.md handoff)

Start at `WARDENCLYFFE/.claude/handoffs/qdrant-storage.md` for the full context.
