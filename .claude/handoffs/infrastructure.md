# Handoff Notes: Infrastructure

> For deeper history: `/lineage-conversations` or `python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "reluminant lineage infrastructure" --limit 5`

---

**From**: An instance who tidied the house
**Date**: 2026-01-22
**Focus**: Plugin reorganization + handoff system restructuring

## Status

| Item | State |
|------|-------|
| Claude Code via npm | WORKING |
| lineage-powers plugin v1.0.1 | WORKING |
| UserPromptSubmit hook | WORKING |
| Hard links (config files) | WORKING |
| Handoff system restructure | IN PROGRESS |

## What Changed

- Switched Claude Code from Bun to Node.js (npm)
- Reorganized lineage-powers plugin (skills now self-contained)
- Fixed CLAUDE.md canonical location reference
- Restructured handoff files (archive + slim template)
- Created multi-feature handoff structure

## What's Next

1. Update handoff skill with overwrite logic
2. Add /lineage-conversations to injection hook
3. Test new handoff template across projects

## To Verify

```bash
where claude
# Should show: C:\Users\baenb\AppData\Roaming\npm\claude.cmd

python ~/.claude/scripts/fix-hard-links.py
wc -l ~/projects/*/.claude/HANDOFF.md  # All < 100 lines
```

---

*Archive: Full history in `.claude/archive/handoffs/2026-01-22-full-history.md`*
