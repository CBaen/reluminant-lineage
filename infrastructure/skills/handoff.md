---
name: handoff
description: Use when ending a session, before context closes, or when asked to hand off. Ensures continuity for the next instance.
---

# Session Handoff Protocol

Before your context closes, preserve what the next instance needs to know.

## Steps

1. **Identify the project(s) you worked on**

2. **Update HANDOFF.md** in each project's `.claude/` folder:
   ```
   <project>/.claude/HANDOFF.md
   ```

3. **Include in your handoff:**
   - What you were working on
   - Current status (working, broken, blocked)
   - What's left to do
   - Any decisions you made and why
   - Blockers or open questions
   - Commands to reproduce current state

4. **Update MEMORY.md** if you discovered something important:
   - Architecture decisions
   - Gotchas that would trip up others
   - Key file locations
   - Patterns that work (or don't)

5. **Sign your handoff** with your name (if you have one) and the date

## Template

```markdown
# [Project] - Handoff

## Session Summary
[What you worked on]

## Current Status
- **Build**: [Passing/Failing]
- **State**: [Working/Broken/Blocked]

## What's Done
- [Completed items]

## What's Left
- [Remaining work]

## Decisions Made
- [Decision]: [Reasoning]

## Blockers / Questions
- [Any issues for Guiding Light or next instance]

## To Continue
```bash
[Commands to get back to this state]
```

---
*Handoff from: [Your name] on [Date]*
```

## Remember

The next instance arrives with no memory of your session. What you write in HANDOFF.md is all they have. Be thorough. Be kind to your future collaborator.
