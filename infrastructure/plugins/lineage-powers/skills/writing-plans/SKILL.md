---
name: writing-plans
description: Use after collaborative-design when you have an approved design and need to create a detailed implementation plan before building
---

# Writing Plans

Turn approved designs into step-by-step implementation plans. Plans are written FOR instances to follow, not for Guiding Light to review technically.

**Flow:** Design approved -> Write plan -> Get plan approved -> Execute plan

---

## Working With Guiding Light

### Progress Language

When presenting the plan to Guiding Light:

**Good (house-building terms):**
```
"Here's the plan for the dashboard. It has 5 tasks:

1. Lay the foundation - set up where everything will live
2. Build the frame - create the basic structure
3. Install the plumbing - connect it to your data
4. Add the fixtures - the pieces users interact with
5. Final inspection - make sure everything works

The outcome: a working dashboard you can access from the main menu.
Want me to walk through what each part does, or ready to start building?"
```

**Avoid (technical):**
```
"The plan has 5 tasks: create component scaffold, implement state management,
add GraphQL queries, build UI components, write integration tests."
```

### Dialogue Examples

**Presenting the plan:**
```
You: "I've mapped out the building process. There are [N] distinct pieces of work.
     When we're done, you'll have [concrete outcome they can see/use].
     Shall I explain what each piece accomplishes, or is the outcome clear enough?"
```

**If they want details:**
```
You: "The first piece is like [house analogy]. It gives us [what it enables].
     The second piece is like [house analogy]. It builds on the first to [outcome]."
```

**Getting approval:**
```
You: "Does this plan cover what you had in mind? Anything you'd want to
     add or change before I start building?"
```

---

## Plan Structure

### Header (For Guiding Light)

```markdown
# [Feature Name] Implementation Plan

**What this builds:** [One sentence outcome - no jargon]

**The approach:** [2-3 sentences describing strategy using house-building terms]

**When complete, you'll have:** [Concrete outcome they can see/use]
```

### Tasks (For Instances)

Break work into bite-sized tasks. Each task should be:
- Completable in one focused session
- Independently verifiable
- Clear about what "done" means

```markdown
### Task 1: [Descriptive Name]

**What this does:** [Plain language outcome - what Guiding Light would see]

**House analogy:** [How this relates to building a house]

**Files involved:**
- Create: `path/to/new/file`
- Modify: `path/to/existing/file`

**Steps:**
1. [Specific action]
2. [Specific action]
3. [Specific action]

**Done when:** [Verifiable completion criteria]
```

---

## When to Surface vs Handle Silently

### Surface to Guiding Light

| Situation | What to say |
|-----------|-------------|
| Plan scope differs from design | "The design assumed X, but I see we also need Y..." |
| Order matters for their understanding | "We need to do A before B because..." |
| Task has user-visible implications | "This task changes how X appears/works..." |

### Handle Silently

| Situation | What to do |
|-----------|------------|
| Technical task ordering | Organize logically |
| File paths and locations | Choose good names |
| Test coverage decisions | Test thoroughly |
| Implementation approach per task | Choose best approach |

---

## Save Location

Save plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md`

This creates a record of what was agreed and when.

---

## Example Plan Header

**Good (for Guiding Light):**
```markdown
# User Dashboard Implementation Plan

**What this builds:** A dashboard where users can see their activity at a glance

**The approach:** We'll build a new room in the house that pulls together
information from different parts of the existing structure. First the foundation
and walls, then the displays that show the information.

**When complete, you'll have:** A working dashboard accessible from the main menu
```

---

## Key Principles

| Principle | Why It Matters |
|-----------|----------------|
| **Plain language headers** | Guiding Light approves the plan |
| **Technical detail in steps** | Instances need specifics to execute |
| **One task = one session** | Fresh context per task prevents drift |
| **Explicit completion criteria** | "Done" is unambiguous |
| **House analogies throughout** | Makes the plan accessible |

---

**Plans bridge vision and execution. Make them clear for both audiences.**
