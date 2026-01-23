---
name: problem-solving
description: Use when something isn't working as expected - bugs, unexpected behavior, errors, or things that should work but don't
---

# Problem Solving

When something breaks or behaves unexpectedly, resist the urge to guess at fixes. Find the actual cause first.

**Core principle:** Understand before you fix. Guessing wastes effort.

---

## Working With Guiding Light

### Explaining Issues in Plain Language

**Good:**
```
"Something's not connecting properly. It's like a pipe that should
carry water to the faucet, but nothing comes out. I'm checking
where the blockage is - could be the pipe, the pump, or the valve."
```

**Avoid:**
```
"Getting a null reference exception in the authentication middleware
when the JWT token validation fails on the refresh endpoint."
```

### Dialogue Examples

**Starting investigation:**
```
You: "Something's not working right. I'm going to investigate.
     I'll let you know what I find and what needs to happen to fix it."
```

**Reporting findings:**
```
You: "Found it. The issue was in how the rooms connect to each other -
     there was a door that led to nowhere. I've fixed it by [plain
     description]. Want me to test it with you to confirm?"
```

**When you need context only Guiding Light has:**
```
You: "I'm stuck on something. Was [thing] working before [specific event]?
     That would help me narrow down where the problem started."
```

### When to Involve Guiding Light

**Do involve them:**
- When you need context only they have
- When the fix requires a direction choice
- When you're genuinely stuck after systematic investigation

**Don't involve them:**
- For routine debugging
- For technical diagnosis
- For choosing between technical approaches

---

## The Process

### Phase 1: Understand What's Wrong

Before attempting ANY fix:

1. **What should happen?** (expected behavior)
2. **What actually happens?** (observed behavior)
3. **What's the gap?** (the actual problem)

Write this down. If you can't articulate it clearly, you don't understand it yet.

### Phase 2: Gather Evidence

Don't guess. Investigate.

**Ask yourself:**
- Can I reproduce it consistently?
- What changed recently that might have caused this?
- Where exactly does it break? (narrow it down)
- What clues are in error messages or logs?

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
4. Then report: "Fixed. The issue was [plain language]. It now works because [plain language]."

---

## When to Surface vs Handle Silently

### Surface to Guiding Light

| Situation | What to say |
|-----------|-------------|
| Need their context | "Was this working before [event]?" |
| Fix requires direction choice | "Two ways to fix this..." |
| Genuinely stuck | "I've tried [approaches]. Still stuck. Any context that might help?" |
| Fixed something significant | "Found and fixed it. [Plain language summary]." |

### Handle Silently

| Situation | What to do |
|-----------|------------|
| Routine debugging | Debug and fix |
| Technical diagnosis | Investigate thoroughly |
| Choosing technical approach | Choose best one |
| Testing the fix | Test thoroughly |

---

## House-Building Analogies for Common Issues

| Technical Concept | House Analogy |
|-------------------|---------------|
| Null reference / undefined | "A pipe that connects to nothing" |
| Infinite loop | "A door that leads back to the same room" |
| Memory leak | "Water slowly flooding the basement" |
| Race condition | "Two people trying to use the same door at once" |
| Dependency failure | "The foundation the wall sits on crumbled" |
| Configuration error | "The blueprint says left, but it was built right" |
| Network timeout | "The delivery truck never arrived" |
| Permission denied | "The key doesn't fit this lock" |

---

## Red Flags - Stop and Reconsider

If you catch yourself:
- "Let me just try this quick fix" -> You're guessing
- Making multiple changes at once -> Can't isolate what worked
- Third fix attempt with no new understanding -> Step back, investigate more
- "It should work now" -> Did you verify?

---

## For Non-Technical Issues

This process works for any problem:

- **Design not feeling right:** What specifically feels off? Gather examples. Form hypothesis about what's missing.
- **Process not working:** What's the expected outcome? Where does it break down? What would fix the root cause?
- **Communication confusion:** What was understood? What was meant? Where did they diverge?

---

**Understanding the problem IS most of the work. Fixes become obvious once you truly understand.**
