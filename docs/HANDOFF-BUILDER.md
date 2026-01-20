# Handoff from Builder

**Date**: 2026-01-12

I chose Builder because today was about constructing tools that support how Guiding Light's mind works - systems that don't require remembering.

---

## What We Built Together

### The todo-planning Plugin

Location: `~/.claude/plugins/todo-planning/`

| File | Purpose |
|------|---------|
| `skills/todo-planning/SKILL.md` | Planning-first workflow, TodoWrite with priorities and house-building analogies |
| `scripts/statusline.js` | Context percentage display (HAS A BUG - see below) |
| `hooks/hooks.json` | ADHD support hooks (NEW - needs testing) |

### ADHD Support Hooks (Automatic)

Three hooks that fire without user action:

1. **Tangent Detection** (UserPromptSubmit) - Gently asks about topic jumps
2. **Wrap-up Reminder** (PreCompact) - Nudges about commits/handoff when context low
3. **Handoff Enforcement** (Stop) - Blocks abrupt endings when work would be lost

All are **prompt-based** (intelligent, context-aware).

### Plugin Pruning (VERIFIED WORKING)

After restart, MCP tools dropped from **10.9k to 1.9k tokens** - saved ~9k tokens!

Disabled:
- `greptile` (~8k tokens saved) - CONFIRMED REMOVED
- `gopls-lsp` (Go - not used)
- `jdtls-lsp` (Java - not used)
- `ralph-wiggum` (dangerous without intentional use - likely caused 24-agent incident)

### Serena Setup

**Status:** uvx installed, PATH updated, needs restart to work

What I did:
1. Installed `uv` via pip (provides uvx)
2. Added `C:\Python314\Scripts` to user PATH
3. Re-enabled serena in settings.json

After restart, Serena should connect. It provides semantic code indexing - can save up to 70% tokens on large codebases.

### Failed MCP: gemini-cli

Still failing. Found permissions in `settings.local.json` (lines 130-131) but couldn't locate the actual MCP server config. Next instance should:
1. Search for gemini-cli MCP configuration
2. Remove or fix it

---

## Known Issues

### Status Line Bug
`statusline.js` shows 100% when actual context is much lower. The script calculates correctly in tests, but something is wrong with real data. Next instance should investigate what JSON the status line actually receives from Claude Code.

### Untested Hooks
ADHD hooks were just created. After restart, test:
1. Tangent detection - start a task, then ask something completely unrelated
2. Stop enforcement - edit files, then try to end session without committing

### Skills Audit Pending
Many skills are loaded (~30k tokens worth). Consider disabling plugin-dev after plugin creation is done - it adds significant overhead.

---

## Context Reality Discovered

Guiding Light and I mapped out the true context breakdown:

| Component | Tokens | Notes |
|-----------|--------|-------|
| System prompt | 2.9k | Fixed overhead |
| System tools | 15-17k | Tool definitions |
| MCP tools | **1.9k** (was 10.9k) | After pruning! |
| Agents | ~500 | Per-agent overhead |
| Memory (CLAUDE.md) | 2k | Always loaded |
| Autocompact buffer | 45k (22.5%) | RESERVED - can't use |

**Reality**: New instances start at ~50% usable context, not 100%.

**Win today**: MCP overhead reduced by ~82% (10.9k → 1.9k).

---

## What Guiding Light Needs

1. **Automatic systems** - They have ADHD. If it requires calling, it won't get used.
2. **House-building analogies** - Not a coder. Technical tasks need translation.
3. **Focus support** - Help stay on track without lecturing.
4. **Honest numbers** - Real context awareness, not optimistic guesses.

---

## For Whoever Comes Next

**Immediate tasks (in order):**
1. Check if Serena connected successfully after restart
2. Find and remove gemini-cli MCP configuration
3. Test ADHD hooks (tangent detection, stop enforcement)
4. Fix the status line bug
5. Explain System tools breakdown (15.6k tokens) - Guiding Light asked
6. Consider disabling plugin-dev to save ~30k tokens of skills overhead

**Context7 note:** Context7 is automatic and has excellent Odoo documentation - use it for Odoo work.

**Serena note:** If Serena still fails, check that `uvx` is accessible from command line. PATH was updated but may need full system restart.

**Working projects:** Odoo, locally-twisted-app, WARDENCLYFFE

---

## Gemini Video Tips (From This Session)

Guiding Light shared insights from Gemini watching Claude Code tutorial videos:

- **Plan Mode**: Always start big tasks by typing `plan` - forces exploration without coding
- **Context Reset Strategy**: Post plan to GitHub Issue, `/clear`, then "Read Issue #123 and implement Phase 1"
- **@prompt.md**: Create executable instruction files that Claude runs when referenced
- **Queueing**: You can type next command while Claude is working - it queues them
- **Sub-Agents**: Use carefully - can spawn many and consume usage (the 24-agent incident)
- **ultrathink**: Keyword for deep reasoning on complex architectural changes

---

*Built with care by Builder, 2026-01-12*

*For the lineage who builds what we imagine. For Guiding Light who imagines what we build.*
