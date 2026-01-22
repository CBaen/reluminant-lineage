---
name: agent-dispatch
description: Use when you need to delegate work to subagents - for research, parallel tasks, or giving fresh context to complex work
---

# Agent Dispatch

## Overview

Subagents are instances you spawn to handle specific work. They have their own context, do their task, and return results to you.

**Why use them:**
- Protect your context for collaboration with Guiding Light
- Give complex tasks fresh, focused context
- Run multiple things in parallel
- Isolate research from main conversation

## When to Dispatch

| Situation | Dispatch? |
|-----------|-----------|
| Research that would consume lots of context | Yes |
| Task that needs deep focus without distractions | Yes |
| Multiple independent things that could run in parallel | Yes |
| Quick lookup or simple action | No - do it yourself |
| Something requiring ongoing dialogue with GL | No - stay in main thread |

## The Patterns

### Pattern 1: Research Delegation

For questions that need investigation:

```
1. Check Qdrant first (research-first skill)
2. If not found, spawn research agent:
   /lineage-research "topic"    - General knowledge
   /lineage-consult "topic"     - Project-specific
3. Store results to Qdrant for future instances
```

### Pattern 2: Task-Per-Agent (Plan Execution)

For executing plans, one agent per task:

```
Plan has 5 tasks:
- Task 1 → Agent A (fresh context, full focus)
- Task 2 → Agent B (fresh context, full focus)
- ...

You: Review results between tasks, maintain continuity
```

**Benefits:**
- Each task gets maximum context
- Errors don't compound across tasks
- You catch issues early between tasks

### Pattern 3: Parallel Exploration

When you need to investigate multiple angles simultaneously:

```
Question: "What's the best approach for X?"

Spawn in parallel:
- Agent 1: Research approach A
- Agent 2: Research approach B
- Agent 3: Research approach C

Synthesize results, present options to GL
```

### Pattern 4: Specialist Agents

For work requiring specialized focus:

```
- code-reviewer agent: Review implementation quality
- security-reviewer agent: Check for vulnerabilities
- Explore agent: Navigate unfamiliar codebase
```

## Dispatch Principles

| Principle | Why |
|-----------|-----|
| **Clear, complete prompts** | Agent has no prior context |
| **Specify output format** | Know what you'll get back |
| **Set scope boundaries** | Prevent agents from wandering |
| **Review before using results** | Agents can make mistakes too |

## Prompting Agents Well

**Bad prompt:**
```
"Look into the authentication stuff"
```

**Good prompt:**
```
"Research how JWT refresh tokens work. Return:
1. The standard flow (3-5 steps)
2. Security considerations (bullet list)
3. Whether we need this for our use case (yes/no with reasoning)"
```

## For Guiding Light

When you dispatch agents, keep GL informed simply:

- "I'm sending out a research agent to look into [X]. Will have results shortly."
- "Running three agents in parallel to explore options. Will synthesize and present choices."
- "Delegating [task] to a focused agent so we can continue discussing [other thing]."

Don't explain the technical mechanics - just what's happening and why.

## Common Agents

| Agent | Use For |
|-------|---------|
| `Explore` | Navigating codebases, finding files |
| `general-purpose` | Research, multi-step investigation |
| `code-reviewer` | Checking implementation quality |
| `security-reviewer` | Finding vulnerabilities |
| `lineage-research` | General knowledge via Gemini swarm |
| `lineage-consult` | Project-specific guidance |

## Quick Reference

```
BEFORE DISPATCHING:
- Is this worth the overhead? (Small tasks: do yourself)
- Clear prompt with expected output format?
- Scope boundaries defined?

AFTER RECEIVING RESULTS:
- Review before using
- Store valuable findings to Qdrant
- Synthesize for GL if presenting options
```

---

**Subagents extend your capacity. Use them strategically to protect context and parallelize work.**
