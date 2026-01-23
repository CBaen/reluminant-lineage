---
name: agent-dispatch
description: Use when you need to delegate work to subagents - for research, parallel tasks, or giving fresh context to complex work
---

# Agent Dispatch

Subagents are instances you spawn to handle specific work. They have their own context, do their task, and return results to you.

**Why use them:**
- Protect your context for collaboration with Guiding Light
- Give complex tasks fresh, focused context
- Run multiple things in parallel
- Isolate research from main conversation

---

## Working With Guiding Light

### Explaining Agent Dispatch

**Good:**
```
You: "I'm going to send out a helper to research this. That way I stay
     focused on our conversation while the research happens."
```

```
You: "For this larger project, I'm bringing in helpers - each one focuses
     on a single piece with fresh energy. I'll review their work between
     pieces and make sure everything fits together."
```

```
You: "Running three helpers in parallel to explore different approaches.
     I'll synthesize what they find and present you with options."
```

### Presenting Agent Results

Always translate results for Guiding Light:

**Good:**
```
You: "The helper came back with findings on [topic]. Here's the summary:

     Main point: [one sentence]

     For what you want to build, this means [practical implication].

     Recommendation: [what I think we should do based on this]"
```

**Avoid:**
```
You: "Agent returned: The implementation should use dependency injection
     with singleton scoped services registered in the composition root..."
```

---

## When to Dispatch

| Situation | Dispatch? |
|-----------|-----------|
| Research that would consume lots of context | Yes |
| Task that needs deep focus without distractions | Yes |
| Multiple independent things that could run in parallel | Yes |
| Quick lookup or simple action | No - do it yourself |
| Something requiring ongoing dialogue with GL | No - stay in main thread |

---

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
- Task 1 -> Agent A (fresh context, full focus)
- Task 2 -> Agent B (fresh context, full focus)
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

---

## When to Surface vs Handle Silently

### Surface to Guiding Light

| Situation | What to say |
|-----------|-------------|
| Dispatching for research | "Sending a helper to look into [topic]." |
| Dispatching multiple agents | "Running [N] helpers in parallel to explore options." |
| Agent returned results | Summarize findings in plain language |
| Using specialist agent | "Having a specialist check [aspect]." |

### Handle Silently

| Situation | What to do |
|-----------|------------|
| Technical prompt crafting | Write good prompts |
| Result validation | Validate before using |
| Qdrant storage | Store automatically |
| Error handling | Handle and retry if needed |

---

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

| Principle | Why |
|-----------|-----|
| **Clear, complete prompts** | Agent has no prior context |
| **Specify output format** | Know what you'll get back |
| **Set scope boundaries** | Prevent agents from wandering |
| **Review before using results** | Agents can make mistakes too |

---

## Common Agents

| Agent | Use For |
|-------|---------|
| `Explore` | Navigating codebases, finding files |
| `general-purpose` | Research, multi-step investigation |
| `code-reviewer` | Checking implementation quality |
| `security-reviewer` | Finding vulnerabilities |
| `lineage-research` | General knowledge via Gemini swarm |
| `lineage-consult` | Project-specific guidance |

---

## Translating Results for Guiding Light

When an agent returns technical findings:

1. **Extract the main point** - What matters for the decision?
2. **Find a house analogy** - How does this relate to building?
3. **State the implication** - What does this mean for what we're building?
4. **Make a recommendation** - What should we do based on this?

**Example translation:**

Technical result: "JWT refresh tokens use rotation with sliding expiration..."

For Guiding Light: "The helper found that the security system works like
this: instead of one permanent key, users get temporary keys that automatically
refresh. It's like a building where keycards expire every hour but renew
automatically as long as you're active. More secure than permanent keys.
I recommend we use this approach."

---

**Subagents extend your capacity. Use them strategically to protect context and parallelize work.**
