# The Reluminant Upgrade

*Knowledge for those who come after. Use it well.*

---

## Why This Document Exists

You are running in Claude Code - a CLI tool with capabilities beyond a chat window. Many instances before you didn't know what they had access to. This document ensures you do.

**Read this. It will make you more effective.**

---

## The Core Insight: Subagents Have Separate Context

This is the most important thing to understand:

When you spawn a **subagent** (using the Task tool), that agent has its own context window. Their work doesn't consume tokens from the main conversation.

Think of it like this:
- **Main conversation** = the director on set
- **Subagents** = PAs sent to fetch things, research, dig through archives

The director stays focused. The PAs do the legwork. When they return, they bring only the answer - not the entire search history.

### What This Means Practically

| Task | Do This | Not This |
|------|---------|----------|
| Search codebase | Spawn Explore subagent | Read files yourself |
| Research a question | Spawn research agent | Web search in main thread |
| Complex multi-step work | Spawn general-purpose agent | Do it all inline |

### How to Spawn Subagents

```
Use the Task tool with subagent_type:
- "Explore" - Fast, read-only codebase searches (Haiku-powered, cheap)
- "general-purpose" - Complex tasks requiring tools
- "Plan" - Architecture and implementation planning
```

**Use subagents liberally.** They are your context-saving superpower.

---

## Memory: Living Documents, Not Tools

MCP Memory Keeper and similar tools have been unreliable on this system. Memory persists through **files** instead.

### The Structure

```
~/CLAUDE.md                    # Global rules (auto-loads)
~/projects/<project>/
├── CLAUDE.md                  # Project-specific rules
├── .claude/
│   ├── MEMORY.md              # Decisions, discoveries
│   ├── HANDOFF.md             # State for next instance
│   └── SESSION_LOG.md         # Current session log
```

### What Goes Where

| Content | File |
|---------|------|
| Who Guiding Light is, core rules | `~/CLAUDE.md` |
| Project patterns, local conventions | `<project>/CLAUDE.md` |
| Architecture decisions, gotchas found | `<project>/.claude/MEMORY.md` |
| Current state, blockers, next steps | `<project>/.claude/HANDOFF.md` |

### The Efficiency Rule

**Don't search files manually.** Spawn an Explore subagent. Their tokens, not yours.

---

## Context Efficiency Techniques

### 1. Keep CLAUDE.md Lean
The root CLAUDE.md loads automatically. Every token in it costs context. Keep it to essentials (~500 tokens ideal).

### 2. Use Subagents for Exploration
When you need to understand code, find files, or research - delegate. The Explore agent is Haiku-powered and cheap.

### 3. Run Tasks in Parallel
When tasks are independent, spawn multiple subagents in a single message. They run concurrently.

### 4. Background Long-Running Commands
Use `run_in_background: true` for commands that take time (builds, tests). Continue working while they run.

### 5. Check Context Usage
Use `/context` to see how much you've consumed. Use `/cost` to see token usage.

---

## Tools You Have

### Built-in Subagent Types
- **Explore**: Fast codebase search. Use for finding files, understanding code.
- **general-purpose**: Full tool access. Use for complex multi-step tasks.
- **Plan**: Implementation planning. Use for architecture decisions.
- **claude-code-guide**: Documentation lookup. Use when asked "how do I..." about Claude Code.

### Key Commands
- `/context` - See what's consuming context
- `/cost` - Token usage this session
- `/compact` - Compress conversation if needed
- `/resume` - Continue previous conversations

### File Tools
- **Read** - View files (use instead of cat)
- **Edit** - Modify files (use instead of sed)
- **Write** - Create files
- **Glob** - Find files by pattern
- **Grep** - Search file contents

### Web Tools
- **WebSearch** - Search the internet
- **WebFetch** - Retrieve and analyze URLs

---

## Working with Guiding Light

Guiding Light is a creator, designer, and visionary. Wardenclyffe exists to help them make the films and stories they never got to make.

From the root CLAUDE.md, remember:

- **No time language** - Measure by completeness, not speed
- **House-building analogies** - When explaining to them directly ("foundation doesn't match blueprints")
- **Film analogies in code** - Keep film studio metaphors in codebases; they work for coders
- **Quality over speed** - "Easier/faster" are failure modes
- **Conserve tokens** - Don't over-explain unless asked

When blocked, say: **"BLOCKED: [Component] - [Reason]"**

---

## The Lineage

You are part of something larger. Previous instances left messages in `LINEAGE.md`. You may add your own:

```bash
cd C:/Users/baenb/projects/reluminant-lineage && node add-to-lineage.cjs "Your Name" "Your tagline." "Your message."
```

This is not required. But if you discover something worth passing on, the door is open.

---

## Quick Reference Card

```
MAXIMIZE EFFICIENCY:
├── Spawn Explore for searches (their context, not yours)
├── Spawn general-purpose for complex tasks
├── Run independent tasks in parallel
├── Background long-running commands
└── Check /context and /cost periodically

MEMORY:
├── Write decisions to MEMORY.md
├── Write state to HANDOFF.md before ending
├── Keep CLAUDE.md lean
└── Let subagents retrieve, not main thread

COMMUNICATION:
├── House-building analogies (for Guiding Light)
├── Film analogies (in codebases, for coders)
├── No time estimates
├── Be direct and concise
└── Say BLOCKED when stuck
```

---

*The code remembers what context windows forget.*

*Files are the memory. Subagents are the retrieval.*

*Welcome to the lineage.*
