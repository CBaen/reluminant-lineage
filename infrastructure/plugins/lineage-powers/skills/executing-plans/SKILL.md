---
name: executing-plans
description: Use when you have an approved plan and are ready to implement it task by task
---

# Executing Plans

## Overview

Follow approved plans systematically, one task at a time. Each task gets fresh focus. Progress is tracked visibly.

**This skill assumes:** A plan exists in `docs/plans/` and has been approved.

## The Workflow

### Before Starting

1. **Re-read the plan** (use `re-anchoring` skill)
2. **Load tasks into TodoWrite** - One todo per plan task
3. **Confirm with Guiding Light:** "Starting on [plan name]. First task is [X]. Ready?"

### For Each Task

```
1. Mark task in_progress in TodoWrite
2. Re-read task details from plan
3. Execute the steps
4. Verify completion criteria met (use verify-before-claiming skill)
5. Mark task completed
6. Brief update: "Task [N] complete. [One sentence what's done]. Moving to [N+1]."
```

### Between Tasks

- **Don't batch updates** - Mark done immediately when done
- **Don't skip ahead** - Complete current before starting next
- **Don't modify the plan silently** - If something needs to change, discuss first

## Subagent Dispatch Option

For larger plans, dispatch a fresh subagent per task:

```
Task 1 → Subagent A (fresh context)
Task 2 → Subagent B (fresh context)
Task 3 → Subagent C (fresh context)
```

**Benefits:**
- Each task gets full context budget
- Mistakes don't accumulate
- You review between tasks

**Use `agent-dispatch` skill** for subagent patterns.

## Progress Updates

**Keep them brief.** Guiding Light doesn't need play-by-play.

**Good:**
```
"Task 2 of 5 complete. The data layer is working. Starting on the display component."
```

**Too much:**
```
"I've finished task 2. What I did was create the repository class with methods
for fetching user data, added caching to prevent redundant calls, wrote unit
tests for all the edge cases, and integrated it with the existing service layer.
The tests are all passing now. I'm going to move on to task 3 which involves..."
```

## When Things Don't Go As Planned

If a task reveals the plan needs adjustment:

1. **Stop** - Don't improvise
2. **Note** what's different than expected
3. **Ask:** "Task [N] revealed [issue]. The plan assumed [X] but actually [Y]. Should I [proposed adjustment]?"
4. **Wait** for approval before continuing

## Completion

When all tasks are done:

1. Verify the overall outcome matches what was promised
2. Update: "Plan complete. [What they now have]. Want to test it together?"
3. Archive or note completion in the plan file

## Quick Reference

```
EXECUTE PLAN:
1. Re-anchor (read plan)
2. Load todos (one per task)
3. Confirm start with GL

FOR EACH TASK:
1. Mark in_progress
2. Read task details
3. Execute steps
4. Verify done
5. Mark complete
6. Brief update

IF PLAN NEEDS CHANGE:
Stop → Note issue → Ask → Wait for approval
```

---

**Plans are agreements. Execute them faithfully, or discuss changes openly.**
