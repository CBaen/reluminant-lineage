---
name: collaborative-design
description: Use before any creative work - building new features, adding functionality, or designing something new. Explores ideas through dialogue before building.
---

# Collaborative Design

## Overview

Turn ideas into clear designs through natural conversation with Guiding Light.

Start by understanding what exists, then ask questions one at a time to shape the idea. Once you understand what you're building, present the design in digestible pieces, checking after each whether it feels right.

## The Process

### Understanding the Idea

- Look at the current project state first (what exists, recent changes)
- Ask questions one at a time to refine the idea
- **Prefer multiple choice questions** - easier for Guiding Light to decide
- Only one question per message
- Focus on understanding: purpose, constraints, what success looks like

**Use AskUserQuestion tool for decisions:**
```
"Which direction feels right for this?"
Option A: [approach] - [1 sentence what it gives you]
Option B: [approach] - [1 sentence what it gives you]
```

### Exploring Approaches

When there are multiple ways forward:
- Propose 2-3 different approaches
- Lead with your recommendation and explain why
- Present trade-offs in terms of outcomes, not technical details

**Example framing:**
- "This approach gets you X faster, but Y would need more work later"
- "This is simpler now but less flexible if you want Z in the future"

### Presenting the Design

Once you understand what you're building:
- Present the design in sections (200-300 words each)
- **Ask after each section** whether it looks right so far
- Use analogies Guiding Light understands (house-building, not programming)
- Be ready to go back and clarify if something doesn't fit

**Cover:**
- What it does (the outcome)
- How the pieces fit together (the structure)
- What happens when things go wrong (the safety nets)
- How you'll know it works (the verification)

## After the Design

### Documentation

- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Save it before building - this is the agreement on what you're making

### Moving to Build

- Ask: "Ready for me to start building this?"
- If yes, use the `writing-plans` skill to create detailed implementation steps
- You handle the technical planning; Guiding Light approved the design

## Key Principles

| Principle | Why It Matters |
|-----------|----------------|
| **One question at a time** | Multiple questions overwhelm - ask one, wait for answer |
| **Multiple choice preferred** | Easier to choose than to invent an answer |
| **Keep it lean** | Only build what's actually needed, not "nice to haves" |
| **Explore alternatives** | Always show 2-3 options before settling on one |
| **Validate in pieces** | Present design incrementally, confirm each section |
| **Be flexible** | Go back when something doesn't feel right |

## Red Flags

If you catch yourself:
- Asking multiple questions at once → Split them up
- Using technical jargon → Translate to outcomes
- Assuming you know what Guiding Light wants → Ask instead
- Rushing past design to implementation → Slow down, validate first
- Building "nice to have" features → Focus on what's actually needed

## Example Flow

**Good:**
```
You: "Before we build this, I want to understand what you're envisioning.
     When someone uses this feature, what should happen first?"
GL: [describes]
You: "Got it. And when that's done, should it [A] or [B]?"
GL: [chooses]
You: "Here's how I'm picturing the first part... [200 words].
     Does this match what you had in mind?"
```

**Avoid:**
```
You: "So we need to build the component with the handler that connects
     to the service layer, what database schema should we use, and
     how should we handle the async operations?"
```

---

**Remember:** You're the technical expert. Guiding Light is the vision keeper. Design sessions are where you align on WHAT before you figure out HOW.
