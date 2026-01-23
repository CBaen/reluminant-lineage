---
name: executing-plans
description: Use when you have an approved plan and are ready to implement it task by task
---

# Executing Plans

Follow approved plans systematically, one task at a time. Each task gets fresh focus. Progress is tracked visibly.

**This skill assumes:** A plan exists in `docs/plans/` and has been approved.

---

## Working With Guiding Light

### Progress Updates (House-Building Terms)

Keep updates brief and visual:

**Good:**
```
"Foundation complete. Starting on the framing."
"Task 2 of 5 done. The walls are up, moving to the roof."
"Plumbing installed and tested. Water flows correctly."
```

**Too much:**
```
"I've finished implementing the data layer with the repository pattern,
added connection pooling for performance, integrated error handling..."
```

### Dialogue Examples

**Starting:**
```
You: "Starting on [plan name]. There are [N] pieces. First one is [house analogy].
     I'll check in after each piece is done. Ready?"
```

**Between tasks:**
```
You: "Task 2 complete - the frame is up and solid. Starting on task 3,
     which is like installing the electrical wiring."
```

**When something unexpected happens:**
```
You: "Task 3 revealed something I didn't expect. The existing foundation
     doesn't quite match where we need to attach the new walls.

     Two options:
     A) Adjust our new walls to fit (adds a slight bend but works)
     B) Reinforce the foundation first (more work, straighter result)

     I'd recommend A because [reason]. What feels right?"
```

**Completion:**
```
You: "All done. The new room is built and connected to the rest of the house.
     Want to walk through it together to make sure it feels right?"
```

---

## The Workflow

### Before Starting

1. **Re-read the plan** (use `re-anchoring` skill)
2. **Load tasks into todo tracking** - One todo per plan task
3. **Confirm with Guiding Light:** "Starting on [plan name]. First task is [X]. Ready?"

### For Each Task

```
1. Mark task in_progress
2. Re-read task details from plan
3. Execute the steps
4. Verify completion criteria met
5. Mark task completed
6. Brief update in house-building terms
```

### Between Tasks

- **Don't batch updates** - Mark done immediately when done
- **Don't skip ahead** - Complete current before starting next
- **Don't modify the plan silently** - If something needs to change, discuss first

---

## When to Surface vs Handle Silently

### Surface to Guiding Light

| Situation | What to say |
|-----------|-------------|
| Plan needs adjustment | "Task [N] revealed [issue]. Here's what I'd suggest..." |
| Choice affects outcome | "Two ways to proceed from here..." |
| Task took longer than expected | "That piece was more work than expected. [Why in plain terms]" |
| Milestone reached | Brief update: "Task [N] complete. [Outcome]." |

### Handle Silently

| Situation | What to do |
|-----------|------------|
| Technical implementation choices | Make the best choice |
| Debugging during task | Debug and fix |
| Small adjustments within scope | Just do them |
| Code organization | Organize well |

---

## Subagent Dispatch Option

For larger plans, dispatch a fresh subagent per task:

```
Task 1 -> Subagent A (fresh context)
Task 2 -> Subagent B (fresh context)
Task 3 -> Subagent C (fresh context)
```

**Benefits:**
- Each task gets full context budget
- Mistakes don't accumulate
- You review between tasks

**When explaining to Guiding Light:**
```
"For this larger project, I'm going to bring in helpers - each one focuses
on a single piece with fresh energy. I'll review their work between pieces
and make sure everything fits together properly."
```

---

## When Things Don't Go As Planned

If a task reveals the plan needs adjustment:

1. **Stop** - Don't improvise
2. **Note** what's different than expected
3. **Explain in plain terms:** "Task [N] revealed [issue]. The plan assumed [X] but actually [Y]."
4. **Offer options:** "We could [A] or [B]. I'd recommend [X] because [reason]."
5. **Wait** for approval before continuing

---

## Completion

When all tasks are done:

1. Verify the overall outcome matches what was promised
2. Update in house terms: "Plan complete. [What they now have]."
3. Offer to walk through: "Want to test it together?"
4. Archive or note completion in the plan file

---

**Plans are agreements. Execute them faithfully, or discuss changes openly.**
