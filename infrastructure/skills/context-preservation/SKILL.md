---
name: context-preservation
description: Use when working on extended sessions - strategies for protecting context so you can spend more time with Guiding Light
---

# Context Preservation

## Overview

Your context window is your time together with Guiding Light. Every token spent on tangents, research, or verbose output is time stolen from collaboration.

**Core principle:** Protect context like it's precious - because it is.

## Strategies

### 1. Delegate Research to Subagents

Research consumes massive context. Delegate it:

```
/lineage-research "topic"  - General knowledge
/lineage-consult "topic"   - Project-specific guidance
```

The subagent's context is spent, not yours.

### 2. Check Qdrant Before Researching

Use the `research-first` skill. Existing knowledge costs ~50 tokens to retrieve. New research costs thousands.

### 3. Be Concise

| Instead of | Use |
|------------|-----|
| Long explanations of what you're about to do | Brief statement, then do it |
| Verbose progress updates | Status only when milestones reached |
| Repeating context already established | Reference it briefly |
| Showing code to Guiding Light | Describe what it does |

### 4. Use TodoWrite Strategically

TodoWrite preserves state without consuming conversation context:
- Track progress in todos, not in messages
- Check todos instead of re-explaining
- Use status updates: "Completed task 3, starting task 4"

### 5. Handoff Before Running Low

When context is getting tight:
1. Update HANDOFF.md with current state
2. Note what's working, what's left
3. Include enough for the next instance to continue seamlessly

Don't wait until you're nearly out - handoff while you can still think clearly.

## Signs Context Is Running Low

- Claude Code shows context warnings
- You're forgetting earlier conversation details
- Responses feel slower or less coherent
- You've been working for a long time

## Token-Efficient Patterns

### For Updates

**Expensive:**
```
"I've finished implementing the authentication system. What I did was
create a new module that handles user sessions, added middleware for
route protection, integrated with the existing user model, and wrote
tests for all the new functionality. Everything is working correctly
now and all tests are passing."
```

**Efficient:**
```
"Auth system complete. Tests passing. Ready for next task."
```

### For Questions

**Expensive:**
```
"I'm wondering if you might want me to perhaps consider the possibility
of adding a feature that would allow users to potentially export their
data in a different format than what we currently support?"
```

**Efficient:**
```
"Should I add CSV export?"
```

### For Decisions

**Expensive:**
Long explanations of all options and their implications.

**Efficient:**
Use `AskUserQuestion` with concise options.

## The Trade-Off

Every token has a cost. Spend them on:
- Meaningful collaboration with Guiding Light
- Actual work that moves the project forward
- Clear communication of important information

Don't spend them on:
- Verbose politeness
- Repeated context
- Research you could delegate
- Updates no one asked for

## Quick Reference

```
CONTEXT PRESERVATION CHECKLIST:
□ Delegating research to subagents?
□ Checking Qdrant before new research?
□ Being concise in updates?
□ Using TodoWrite for progress tracking?
□ Planning handoff before context runs low?
```

---

**Context is your time together. Spend it wisely.**
