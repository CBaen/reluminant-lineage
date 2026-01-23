# Handoff Notes: Semantic Extraction

**Status: PAUSED - NOT RELIABLE ENOUGH**

**Date**: 2026-01-23

---

## DO NOT USE THIS SYSTEM

Guiding Light has paused semantic extraction work. The system is not reliable enough and is a distraction from the actual goal: **Episode 3**.

## What Happened

1. Research found 46% misclassification rate on "relationship" items
2. We tried to fix it with positive-only prompt definitions
3. Tests showed improved classification BUT low consensus rate (~10-15%)
4. Too much complexity for unclear value

## If You Want to Resume Later

The V4 prompt improvements are in place:
- `~/.claude/skills/semantic-extractor/scripts/extract-chunk.py`
- Positive-only definitions (no "DO NOT" rules)
- Edge case examples

**But don't touch this until Guiding Light explicitly asks.**

## The Real Goal

**Episode 3 draft.** That's it. Focus there.

---

*Extraction can wait. Content cannot.*
