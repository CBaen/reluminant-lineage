# Lineage Powers

Workflow skills for the Reluminant Lineage.

**Full documentation:** See `docs/LINEAGE_POWERS.md` in the reluminant-lineage repo.

## Skills Location

**Skills have moved to `infrastructure/skills/`** where they are auto-discovered by Claude Code.

The plugin structure remains here for potential future use (if plugin-based skill discovery improves), but skills are installed to the main skills folder via junction to `~/.claude/skills/`.

## Quick Reference

| Skill | Purpose | Location |
|-------|---------|----------|
| collaborative-design | Ideas → designs through dialogue | `skills/collaborative-design/` |
| writing-plans | Designs → implementation plans | `skills/writing-plans/` |
| executing-plans | Follow plans task by task | `skills/executing-plans/` |
| problem-solving | Find root causes before fixing | `skills/problem-solving/` |
| verify-before-claiming | Evidence before assertions | `skills/verify-before-claiming/` |
| re-anchoring | Check bearings before tasks | `skills/re-anchoring/` |
| research-first | Check Qdrant before researching | `skills/research-first/` |
| context-preservation | Protect context in long sessions | `skills/context-preservation/` |
| agent-dispatch | Delegate work effectively | `skills/agent-dispatch/` |

All paths above are relative to `infrastructure/` in the reluminant-lineage repo.
