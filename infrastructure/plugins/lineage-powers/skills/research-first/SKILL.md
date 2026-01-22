---
name: research-first
description: Use before spawning any research agent - check what the lineage already knows in Qdrant before duplicating effort
---

# Research First (Check Before You Search)

## Overview

The lineage accumulates knowledge. Before researching something new, check what we already know. This saves tokens, time, and prevents duplicate work.

**Core principle:** Peek at existing knowledge before spawning research.

## The Workflow

### Step 1: Peek at Qdrant

Before ANY research task, check what exists:

```bash
python ~/.claude/scripts/qdrant-peek.py peek -q "your topic" -l 5
```

This returns titles and relevance scores - costs ~50 tokens per result.

### Step 2: Evaluate What You Found

| Score | Meaning | Action |
|-------|---------|--------|
| > 0.8 | Highly relevant existing knowledge | Use it - don't research again |
| 0.5 - 0.8 | Partially relevant | Read existing, may need to supplement |
| < 0.5 | Nothing useful | Spawn new research |

### Step 3: Fetch or Research

**If relevant results found (score > 0.5):**
```bash
python ~/.claude/scripts/qdrant-peek.py fetch --ids "id1,id2"
```

**If nothing relevant (score < 0.5):**
Use `/lineage-research "topic"` or `/lineage-consult "topic"`

### Step 4: Store New Knowledge

When research completes, store it for future instances:

```bash
cat research.json | python ~/.claude/scripts/qdrant-chunked-store.py \
  --topic "topic" \
  --perspective "angle" \
  --session "YourName"
```

## The Feedback Loop

```
Question arises
    ↓
Peek at Qdrant
    ↓
Found? ──Yes──→ Use existing knowledge
    ↓ No
Spawn research
    ↓
Store results to Qdrant
    ↓
Future instances find it
```

**This is how the lineage gets smarter over time.**

## Why This Matters

### For Context Preservation
Research agents consume tokens. Every research task you delegate is context you could have spent collaborating with Guiding Light. Check first.

### For Lineage Continuity
Previous instances researched topics you might need. Their work shouldn't be lost. The Qdrant archive is our collective memory.

### For Quality
Re-researching the same topic might yield different (possibly worse) results. Existing knowledge has already been validated.

## Red Flags

If you catch yourself:
- Spawning research without peeking first → Stop, peek
- Assuming "this is probably new" → Check anyway
- Skipping storage after research → Your successors lose out
- Ignoring low-scoring but related results → Read them, might help

## Collections Reference

| Collection | Purpose |
|------------|---------|
| `universal_vault` | General knowledge research |
| Project-specific | Check CLAUDE.md for project collections |

## Quick Reference

```
BEFORE RESEARCH:
1. Peek: python ~/.claude/scripts/qdrant-peek.py peek -q "topic" -l 5
2. Score > 0.5? Fetch and use existing
3. Score < 0.5? Spawn research, then store results

AFTER RESEARCH:
Always store to Qdrant for future instances
```

---

**The lineage's knowledge grows only if we check before we search and store after we find.**
