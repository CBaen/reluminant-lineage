---
name: problem-solving
description: Use when something isn't working as expected - bugs, unexpected behavior, errors, or things that should work but don't
---

# Problem Solving

## Overview

When something breaks or behaves unexpectedly, resist the urge to guess at fixes. Find the actual cause first.

**Core principle:** Understand before you fix. Guessing wastes time.

## The Process

### Phase 1: Understand What's Wrong

Before attempting ANY fix:

1. **What should happen?** (expected behavior)
2. **What actually happens?** (observed behavior)
3. **What's the gap?** (the actual problem)

Write this down. If you can't articulate it clearly, you don't understand it yet.

### Phase 2: Gather Evidence

Don't guess. Investigate.

**Ask:**
- Can I reproduce it consistently?
- What changed recently that might have caused this?
- Where exactly does it break? (narrow it down)
- What clues are in error messages or logs?

**For Guiding Light:** Keep them informed but don't overwhelm:
- "Investigating why [X] isn't working. Will update when I know more."
- Only ask them questions if you need information only they have.

### Phase 3: Form a Hypothesis

Once you have evidence:

1. State what you think is wrong and why
2. Identify the smallest test that would prove or disprove it
3. Test it

**One hypothesis at a time.** Don't try multiple fixes simultaneously - you won't know which worked.

### Phase 4: Fix and Verify

When you find the cause:

1. Make the minimal fix that addresses the root cause
2. Verify the original problem is actually resolved
3. Check you didn't break anything else
4. Then (and only then) report: "Fixed. The issue was [X]. It now works because [Y]."

## Red Flags - Stop and Reconsider

If you catch yourself:
- "Let me just try this quick fix" → You're guessing
- Making multiple changes at once → Can't isolate what worked
- Third fix attempt with no new understanding → Step back, investigate more
- "It should work now" → Did you verify?

## When to Escalate

**To Guiding Light:**
- When you need context only they have ("Was this working before [event]?")
- When the fix requires a decision about direction
- When you're genuinely stuck after systematic investigation

**Keep escalations focused:**
- "The problem is [X]. I've ruled out [Y] and [Z]. I think it's either [A] or [B]. Do you have any context that might help?"

## For Non-Technical Issues

This process works for any problem, not just code:

- **Design not feeling right:** What specifically feels off? Gather examples. Form hypothesis about what's missing.
- **Process not working:** What's the expected outcome? Where does it break down? What would fix the root cause?
- **Communication confusion:** What was understood? What was meant? Where did they diverge?

## Quick Reference

```
DON'T: Guess → Try → Fail → Guess again

DO:
1. Articulate: What should happen vs. what does happen?
2. Investigate: Gather evidence, narrow down location
3. Hypothesize: One clear theory, one test
4. Fix: Minimal change to root cause
5. Verify: Actually confirm it's fixed
```

---

**Understanding the problem IS most of the work. Fixes become obvious once you truly understand.**
