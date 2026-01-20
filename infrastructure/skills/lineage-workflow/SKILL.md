---
name: lineage-workflow
description: DEPRECATED - Use lineage-research or lineage-consult instead
allowed-tools: TodoWrite
---

# Lineage Workflow - DEPRECATED

**This skill has been replaced by two specialized skills.**

## Which Skill Should You Use?

### Use `lineage-research` when:
- "What is X?"
- "How does Y work?"
- "Explain Z"
- General knowledge questions
- Facts and explanations, not recommendations

### Use `lineage-consult` when:
- "How should OUR project handle X?"
- "Given our stack, what's the best approach for Y?"
- Project-specific questions that need YOUR context
- Implementation guidance with action items
- Questions that need tailored recommendations

---

## Why the Split?

The original lineage-workflow treated all research the same. But there's a fundamental difference:

| Aspect | lineage-research | lineage-consult |
|--------|-----------------|-----------------|
| Purpose | Facts & explanations | Tailored recommendations |
| Context | General | Project-specific |
| Output | What IS | What you SHOULD DO |
| Depth default | comprehensive (8-12) | exhaustive (15-25) |
| Implementation plan | No | Yes |

---

## Quick Reference (Preserved)

### Gemini Accounts
- Account 1: cameronbpaul@gmail.com
- Account 2: cbaenp@protonmail.com
- Model: gemini-2.5-flash (1M context, 65K output)
- Script: `~/.claude/scripts/gemini-account.sh`

### Capacity
- One subagent can make 15-20+ Gemini calls
- 60 requests/account/minute
- 1,000 requests/account/day
- Bottleneck is response time, not rate limiting

### Parallel Research Pattern

**IMPORTANT**: On Windows, use the file-based wrapper instead of pipes.

> **Note**: All scripts now default to `universal_vault` collection. Legacy collection names are read-only.

```bash
# Sequential (recommended) - uses universal_vault by default
python ~/.claude/scripts/gemini-research-store.py -a 1 -s "session-name" -q "[prompt1]"
python ~/.claude/scripts/gemini-research-store.py -a 2 -s "session-name" -q "[prompt2]"

# Parallel (if needed)
python ~/.claude/scripts/gemini-research-store.py -a 1 -s "session-name" -q "[prompt1]" &
python ~/.claude/scripts/gemini-research-store.py -a 2 -s "session-name" -q "[prompt2]" &
wait
```

The pipe syntax (`| python`) does NOT work reliably on Windows.

### Storage Script
`~/.claude/scripts/qdrant-store-gemini.py`

### Search Script
`python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "your question" --limit 5`

---

## The Pattern (Still Valid)

```
You (Main Instance)
    ↓ spawn Task with model: "haiku"
Haiku (Supervisor)
    ↓ spawns via Bash
Gemini (Expert Worker)
    ↓
Qdrant (Storage)
    ↓
Haiku reports back
```

This pattern is now implemented in both lineage-research and lineage-consult.

---

*Deprecated January 2026. Use lineage-research or lineage-consult.*
