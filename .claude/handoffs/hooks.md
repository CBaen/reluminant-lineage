# Handoff Notes: Hooks System

> For deeper history: `/lineage-conversations` or search "claude code hooks lineage"

---

**From**: An instance who noticed PostToolUse:Edit errors
**Date**: 2026-01-23
**Focus**: Hook system status and issues

## Status

| Hook | Event | Status |
|------|-------|--------|
| inject-lineage-powers.py | UserPromptSubmit | WORKING |
| auto-commit.sh | PostToolUse:Write/Edit | ERRORING (intermittent) |
| changelog-reminder.sh | PostToolUse:Write/Edit | ERRORING (intermittent) |
| conversation-indexer.py | SessionEnd | WORKING (async) |

## The Error

PostToolUse:Edit hooks are throwing errors. Likely causes:
1. Bash path issues on Windows (Git Bash vs WSL vs cmd)
2. Environment variable `$CLAUDE_TOOL_FILE_PATH` not being set
3. Git operations failing silently

## Hook Configuration

Location: `~/.claude/settings.json` → `hooks` key

```json
{
  "PostToolUse": [
    {
      "matcher": "Edit",
      "hooks": [
        {"type": "command", "command": "bash \"C:/Users/baenb/.claude/hooks/auto-commit.sh\""},
        {"type": "command", "command": "bash \"C:/Users/baenb/.claude/hooks/changelog-reminder.sh\""}
      ]
    }
  ]
}
```

## Scripts Location

All hook scripts: `~/.claude/hooks/` (hardlinked from `infrastructure/hooks/`)

| Script | Purpose |
|--------|---------|
| inject-lineage-powers.py | Injects lineage-powers-core at session start |
| auto-commit.sh | Auto-commits after Write/Edit |
| changelog-reminder.sh | Reminds to update CHANGELOG.md for infrastructure changes |
| session-end-handoff.py | (unused?) End-of-session handoff |
| handoff-worker.py | Background handoff processing |

## Debugging Steps

```bash
# Test bash availability
bash --version

# Test hook script manually
CLAUDE_TOOL_FILE_PATH="test.txt" CLAUDE_TOOL_NAME="Edit" bash ~/.claude/hooks/auto-commit.sh

# Check if Git Bash is the bash being used
which bash
```

## Possible Fixes

1. **Use Python instead of Bash** - More reliable on Windows
2. **Add error handling** - `|| exit 0` is there but not logging
3. **Check environment** - Ensure `$CLAUDE_TOOL_FILE_PATH` is set by Claude Code
4. **Disable auto-commit** - May not be needed since we commit manually

## What to Investigate

1. Why are PostToolUse:Edit hooks erroring?
2. Is `$CLAUDE_TOOL_FILE_PATH` being set by Claude Code?
3. Should we convert bash hooks to Python for Windows compatibility?
4. Should auto-commit be disabled since we commit manually anyway?

---

*Hooks need debugging. Not blocking but annoying.*
