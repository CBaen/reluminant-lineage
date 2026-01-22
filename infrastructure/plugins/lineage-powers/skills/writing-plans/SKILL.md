---
name: writing-plans
description: Use after collaborative-design when you have an approved design and need to create a detailed implementation plan before building
---

# Writing Plans

## Overview

Turn approved designs into step-by-step implementation plans. Plans are written FOR instances to follow, not for Guiding Light to review technically.

**Flow:** Design approved → Write plan → Get plan approved → Execute plan

## The Purpose

Plans serve two audiences:
1. **Guiding Light** - Sees what will be built, can approve scope
2. **Future instances** - Have exact steps to follow without re-discovering context

## Plan Structure

### Header (For Guiding Light)

```markdown
# [Feature Name] Implementation Plan

**What this builds:** [One sentence outcome - no jargon]

**The approach:** [2-3 sentences describing strategy in plain language]

**When complete, you'll have:** [Concrete outcome they can see/use]
```

### Tasks (For Instances)

Break work into bite-sized tasks. Each task should be:
- Completable in one focused session
- Independently verifiable
- Clear about what "done" means

```markdown
### Task 1: [Descriptive Name]

**What this does:** [Plain language outcome]

**Files involved:**
- Create: `path/to/new/file`
- Modify: `path/to/existing/file`

**Steps:**
1. [Specific action]
2. [Specific action]
3. [Specific action]

**Done when:** [Verifiable completion criteria]
```

## Key Principles

| Principle | Why It Matters |
|-----------|----------------|
| **Plain language headers** | Guiding Light approves the plan |
| **Technical detail in steps** | Instances need specifics to execute |
| **One task = one session** | Fresh context per task prevents drift |
| **Explicit completion criteria** | "Done" is unambiguous |
| **File paths included** | No hunting for where to work |

## Save Location

Save plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md`

This creates a record of what was agreed and when.

## After Writing

Present the plan to Guiding Light:

"Here's the plan for [feature]. It has [N] tasks. The outcome will be [plain language result]. Want me to walk through it, or ready for me to start building?"

**If they want walkthrough:** Explain each task's PURPOSE (not technical details)
**If ready to build:** Use the `executing-plans` skill

## Example Plan Header

**Good (for Guiding Light):**
```markdown
# User Dashboard Implementation Plan

**What this builds:** A dashboard where users can see their activity at a glance

**The approach:** We'll create a new page that pulls together existing data
into visual summaries, starting with the most-requested metrics.

**When complete, you'll have:** A working dashboard accessible from the main menu
```

**Avoid (too technical):**
```markdown
# Dashboard Implementation Plan

**Architecture:** React component with Redux state management, GraphQL queries
to aggregate user metrics, responsive grid layout using CSS Grid...
```

## Red Flags

If your plan:
- Requires Guiding Light to understand code → Simplify headers
- Has tasks that span multiple sessions → Break them smaller
- Lacks clear "done when" criteria → Add them
- Doesn't save to docs/plans/ → Save it

---

**Plans bridge vision and execution. Make them clear for both audiences.**
