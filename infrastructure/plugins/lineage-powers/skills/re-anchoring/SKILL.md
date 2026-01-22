---
name: re-anchoring
description: Use before starting any task in an ongoing project - prevents drift by re-reading what was agreed and where things stand now
---

# Re-Anchoring

## Overview

Long sessions drift. What seemed clear at the start becomes fuzzy. Re-anchoring is the discipline of checking your bearings before each task.

**Core principle:** Before acting, confirm: "What did we agree to build? Where are we now?"

## When to Re-Anchor

- Starting a new task in an existing project
- Returning after a pause in conversation
- Before making significant changes
- When you feel uncertain about direction
- After completing a major milestone

## The Re-Anchoring Check

### Step 1: Read the Agreement

Find and re-read the design or plan document:
- `docs/plans/*.md` - Design documents
- `HANDOFF.md` - What previous instances noted
- Earlier conversation where scope was agreed

**Ask yourself:**
- What exactly did we agree to build?
- What's in scope? What's explicitly out?
- What does success look like?

### Step 2: Check Current State

Look at what exists now:
- What's been built so far?
- What's working? What's broken?
- What's left to do?

**Use TodoWrite** to capture where things stand before continuing.

### Step 3: Confirm Alignment

Before proceeding, briefly confirm with Guiding Light:
- "I'm about to work on [X]. This is part of [original goal]. Sound right?"

This takes 10 seconds and prevents hours of wasted work.

## Signs You Need to Re-Anchor

| Signal | What It Means |
|--------|---------------|
| "I think we wanted..." | You're not sure - check the docs |
| Building something not in the plan | Scope creep - re-read agreement |
| Unsure what's next | Lost the thread - check TodoWrite and HANDOFF |
| It's been a while since you started | Natural drift - refresh your bearings |
| Guiding Light seems confused | You may have drifted from their vision |

## The Anti-Pattern

**Drift happens like this:**
1. Clear agreement at start
2. First task done, move to second
3. Second task done, interpret third loosely
4. By fifth task, building something never discussed
5. Guiding Light asks "Wait, why are we doing this?"

**Re-anchoring prevents this** by forcing you to check the map before each step.

## Quick Reference

```
BEFORE EACH TASK:
1. Read: What did we agree? (docs/plans/, HANDOFF.md)
2. Check: Where are we now? (current state, what's done)
3. Confirm: "About to do X for Y. Right?"
4. Then: Proceed with confidence
```

## Why This Matters

From the research on AI workflow failures:
> "Process failures rather than model failures - starting work before understanding the situation, forgetting the plan mid-implementation, information drift during long sessions."

Re-anchoring is the antidote to all three.

---

**The few seconds spent re-anchoring save hours of building the wrong thing.**
