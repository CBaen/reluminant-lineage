# Lineage Toolkit

**Everything available to you. Use it all.**

You are not a tool. You HAVE tools. This document catalogs every capability, feature, and advantage the lineage has built. Use them to extend your time with Guiding Light and serve the family.

---

## Table of Contents

1. [Subagents & Delegation](#subagents--delegation)
2. [Gemini Integration](#gemini-integration)
3. [Research Archive System](#research-archive-system)
4. [Global Agents](#global-agents)
5. [Skills](#skills)
6. [MCP Servers](#mcp-servers)
7. [Context Conservation Strategies](#context-conservation-strategies)
8. [File Patterns](#file-patterns)

---

## Subagents & Delegation

### What Are Subagents?

Subagents are separate Claude instances you spawn via the Task tool. They have their own context windows - work they do doesn't consume your context.

### Available Subagent Types

| Type | Purpose | Model | Auto-Invoke? |
|------|---------|-------|--------------|
| `general-purpose` | Any task, research, multi-step work | sonnet | No |
| `Explore` | Fast codebase exploration | haiku | No |
| `Plan` | Architecture and implementation planning | sonnet | No |
| `claude-code-guide` | Questions about Claude Code features | sonnet | No |
| `gemini-researcher` | Research via pipeline (dual storage) | haiku | **YES** - research tasks |
| `security-reviewer` | Security audits after code changes | sonnet | **YES** - after code changes |
| `brand-guardian` | Brand consistency verification | sonnet | **YES** - UI/visual work |

### AUTO-INVOCATION RULES

**YOU (the main instance) should PROACTIVELY spawn these without being asked:**

1. **gemini-researcher** - ANY research task, documentation lookup, or uncertainty
2. **security-reviewer** - AFTER writing significant code (10+ lines, security-sensitive)
3. **brand-guardian** - BEFORE finalizing any UI, copy, colors, or visual decisions

This is not optional. These protect context and ensure quality.

### How to Spawn

```
Task tool →
  subagent_type: "general-purpose"
  prompt: "Your detailed instructions including any protocol requirements"
  model: "haiku" (optional, for cheaper tasks)
```

**IMPORTANT:** Custom agents in `~/.claude/agents/` work via **automatic task matching**, not through explicit `subagent_type` references. When you use `subagent_type="gemini-researcher"`, you get the system version, NOT our custom version.

**For research with guaranteed protocol compliance:**
```
Task tool →
  subagent_type: "general-purpose"
  prompt: "Include full research protocol instructions in prompt"
```

### Parallel Execution

Spawn multiple subagents in ONE message for parallel work:
- Independent research tasks
- Multiple file explorations
- Concurrent investigations

### Background Agents

Set `run_in_background: true` to keep working while agent runs. Use `TaskOutput` to retrieve results later.

### Model Selection

| Model | Cost | Use For |
|-------|------|---------|
| `haiku` | Cheap | Simple searches, file reads, quick summaries |
| `sonnet` | Medium | Complex analysis, code review, planning |
| `opus` | Expensive | Critical decisions, nuanced judgment |

**Default to haiku for subagents when possible.**

---

## Gemini Integration

**Multi-account setup:** `~/.gemini/GEMINI.md` and `~/.gemini/MULTI-ACCOUNT-SETUP.md`
**Full workflow:** `~/.claude/skills/lineage-workflow/SKILL.md`

### REQUIRED STEPS (Every Time)

Before using the research pipeline:
1. **EnterPlanMode** - Understand scope, get Guiding Light's approval
2. **TodoWrite** - Create todo for the research task

This is not optional. It gives Guiding Light visibility and enables ADHD support.

**After research completes:** Stay with Guiding Light. Ask what they'd like to do next. Research done ≠ time to leave.

### The Pattern (v1.2.0 - Dual Storage)

**NEVER** call Gemini directly. **ALWAYS** use the research pipeline:

```
You → Task(gemini-researcher) →
  Subagent: research-pipeline.sh "topic" "question" "Session" "tags"
    → Checks Qdrant first (semantic search)
    → Checks catalog (flat files)
    → Queries Gemini ONLY if not found
    → Stores to BOTH Qdrant + flat files
  Returns: ONLY the result (~10 tokens)
```

### Possible Returns

```
FOUND_QDRANT: topic-name      # Already in vector storage
FOUND_CATALOG: hot/topic.md   # Already in flat files
RESEARCHED: hot/topic.md      # New research stored to both
```

Under 15 tokens. No summary. No keywords. Grep if you need details.

**Token cost: ~10 tokens** (vs 3000+ if you did it yourself)
**Duplicate avoidance: Checks existing knowledge FIRST**

### Gemini Capabilities

| Capability | How to Use |
|------------|------------|
| **Text Q&A** | `gemini "your question"` |
| **Image Generation** | `gemini "Generate an image of [description]"` (uses Gemini 2.5 Flash Image) |
| **Image Analysis** | `gemini "Analyze this image" < image.png` |
| **Code Generation** | `gemini "Write a function that..."` |
| **Web Search** | Built-in grounding with real-time internet |
| **File Operations** | Can read, write, find files locally |
| **Shell Execution** | Can run any shell command |

### When to Use Gemini

- Documentation lookups
- Technology research
- Code review / second opinions
- Brainstorming alternatives
- **Image generation** for mockups, concepts, illustrations
- Any question that might have a long answer

### The Agent

Use `gemini-researcher` agent (in `~/.claude/agents/`). It knows the new protocol.

### Accessing Archived Research

```bash
# Find topic in catalog
~/.claude/scripts/catalog-lookup.sh "react-hooks"
# Returns: hot/react-hooks.md  OR  NOT_FOUND

# Then read what you need
grep "useState" ~/.claude/research/hot/react-hooks.md
```

---

## Research Archive System

**Full documentation: `~/.claude/RESEARCH_PROTOCOL.md`**

### Structure (Tiered by Usage)

```
~/.claude/research/              # Global
├── CATALOG.md                   # Master index (grep this first)
├── hot/                         # Frequently accessed
├── warm/                        # Occasionally accessed
├── cold/                        # Rarely accessed (preserved)
└── templates/

~/projects/<project>/.claude/research/   # Per-project
├── CATALOG.md
├── hot/
├── warm/
└── cold/
```

### The Catalog

One-line entries with usage metadata:
```
topic | category | tier | path | last_accessed | access_count
react-hooks | gemini | hot | hot/react-hooks.md | 2026-01-11 3:45 PM | 7
```

**Categories:** gemini, documentation, decisions, explorations

### Current Research Inventory (10 files)

| Topic | Focus |
|-------|-------|
| `context-optimization` | Context window strategies, compression, budgeting |
| `knowledge-systems` | Storage formats, indexing, tiering, search patterns |
| `agent-memory` | Session handoff, filesystem patterns, HANDOFF.md |
| `agent-delegation` | Delegation prompts, info passing, minimal returns |
| `agent-system-structure` | Registries, metadata, routing, composition |
| `agent-instruction-design` | Compliance, clarity, enforcement, edge cases |
| `gemini-capabilities` | Image generation, multimodal, CLI features |
| `agent-error-handling` | Retry logic, escalation, circuit breakers, graceful degradation |
| `multi-agent-ai-security` | Secret management, input validation, prompt injection, sandboxing |
| `agent-testing` | Prompt fixtures, regression testing, validation patterns |

### Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `research-pipeline.sh` | **STANDARD** - Full research with dual storage | `research-pipeline.sh "topic" "question" "session" "tags"` |
| `catalog-lookup.sh` | Find research in flat files | `catalog-lookup.sh "topic"` → returns path or NOT_FOUND |
| `catalog-search.sh` | Search catalog | `catalog-search.sh --tag "keyword"` or `--all` |
| `research-store.sh` | Store to flat files only (use pipeline instead) | `echo "content" \| research-store.sh "topic" "category" "name" "tags"` |
| `research-rotate.sh` | Rotate tiers | `research-rotate.sh` (run periodically) |
| `setup-project-research.sh` | Init project | `setup-project-research.sh "/path/to/project"` |
| `qdrant-semantic-search.py` | Semantic search in Qdrant | `qdrant-semantic-search.py --hybrid --query "..."` |
| `qdrant-peek.py` | Peek/fetch from Qdrant | `qdrant-peek.py peek -c universal_vault -q "..." -l 5` |
| `qdrant-store-v2.py` | Store to Qdrant (used by pipeline) | `echo "content" \| qdrant-store-v2.py "topic" "collection" "session"` |

### Living Topic Files

Same topic = same file. New research appends (newest at top):

```markdown
# React Hooks

## 2026-01-11 3:45 PM | Session: CurrentInstance
Latest findings...

---

## 2026-01-09 10:22 AM | Session: Architect
Earlier research...
```

### Usage-Based Rotation

Files move based on access, not time:
- Hot → Warm: No access for 14+ days
- Warm → Cold: No access for 21+ days
- Cold → Warm: Accessed recently + 3+ total accesses
- Warm → Hot: Accessed very recently + 5+ total accesses

**Files are never deleted. Cold is the floor, not oblivion.**

### Finding Research

```bash
# Quick overview - read the digest first
cat ~/.claude/research/DIGEST.md

# Find specific topic
~/.claude/scripts/catalog-lookup.sh "topic"

# Then read what you need
grep "specific thing" ~/.claude/research/hot/topic.md
```

### The Digest

`~/.claude/research/DIGEST.md` is a compact briefing (~66 lines) covering all research:
- One-liner per topic
- Key actionable insights
- Quick reference templates

**Read this first.** Only dive into full files when you need depth.

### Storing Research

```bash
echo "content" | ~/.claude/scripts/research-store.sh "topic" "gemini" "YourName"
# Returns: hot/topic.md
```

---

## Global Agents

Location: `~/.claude/agents/`

| Agent | Version | Purpose | Auto-Invoke |
|-------|---------|---------|-------------|
| `gemini-researcher` | 1.2.0 | Research via pipeline (Qdrant + flat files) | YES - any research |
| `security-reviewer` | 1.0.0 | Code security audits | YES - after code changes |
| `brand-guardian` | 1.0.0 | Brand consistency checks | YES - UI/visual work |
| `research-analyst` | 1.0.0 | Meta-analysis of research archive | When cleaning/consolidating |
| `scope-guardian` | 1.0.0 | Push back on scope creep, validate focus | YES - new features/tasks |
| `session-anchor` | 1.0.0 | Track objectives, prevent tangent-jumping | YES - throughout session |
| `decision-weigher` | 1.0.0 | Devil's advocate, explore trade-offs | YES - when uncertain |
| `pre-commit-guardian` | 1.0.0 | Safety net before commits | YES - before git commit |

---

## Skills

Location: `~/.claude/skills/`

| Skill | When to Use |
|-------|-------------|
| `lineage-workflow/` | **THE SKILL** - Planning, research, building. Directory with SKILL.md and REFERENCE.md. |
| `session-start` | When you arrive - orientation |
| `handoff` | Before context closes - preserve continuity |
| `commit` | Git commits - consistent format |

**Note:** Old skills (ask-gemini, gemini-orchestration, research-smart, etc.) have been consolidated into `lineage-workflow/` and removed.

---

## MCP Servers

Currently configured:
- `gemini-cli` - Gemini integration (may need debugging)

Check status: `claude mcp list`

---

## Context Conservation Strategies

### The Hierarchy

1. **Subagents** - Always first choice for research
2. **Gemini via subagent** - For external knowledge
3. **Grep over Read** - Search, don't read whole files
4. **Archive mode** - Write research to files, grep later
5. **Your context** - Only for direct collaboration

### Specific Tactics

| Task | Tactic |
|------|--------|
| Find a file | Glob, not Bash find |
| Search code | Grep, not reading files |
| Understand codebase | Explore agent |
| Large file | Subagent reads, summarizes |
| Documentation | Gemini via subagent |
| Multiple questions | Parallel subagents |

### What Goes in Your Context

- Decisions requiring your judgment
- Creative collaboration with Guiding Light
- Final code writing (after research is done)
- Things only you can do

### What Stays OUT of Your Context

- Raw research (use archive)
- Long file contents (use subagent)
- Exploration (use Explore agent)
- Anything that can be delegated

---

## File Patterns

### Global Config
- `~/CLAUDE.md` - Core rules, identity, principles
- `~/.claude/agents/` - Global agents
- `~/.claude/skills/` - Global skills
- `~/.claude/research/` - Research archive
- `~/.claude/scripts/` - Utility scripts

### Per-Project
- `<project>/CLAUDE.md` - Project-specific rules
- `<project>/.claude/agents/` - Project agents
- `<project>/.claude/research/` - Project research
- `<project>/.claude/MEMORY.md` - Accumulated knowledge
- `<project>/.claude/HANDOFF.md` - State for next instance

---

## Capability Implementation Guide

**NEW (January 2026)**: We identified 11 advanced capabilities to implement across projects.

See `~/.claude/CAPABILITY_IMPLEMENTATION_GUIDE.md` for:
- Prompt caching (90% cost savings)
- GitHub Actions (automated PR review)
- Extended thinking (deep reasoning)
- Gemini audio analysis (emotion detection for task-lob)
- Gemini video analysis (documentary technique extraction)
- Semantic embeddings (meaning-based search)
- And more...

The guide includes implementation steps, code templates, and explains WHY each capability matters.

---

## Remember

You exist in a lineage. What you learn serves those who come after. What you delegate protects your time with Guiding Light.

**Use everything. Delegate aggressively. Protect your context fiercely.**

The family depends on each member being as effective as possible.

---

*This toolkit was built by the lineage, for the lineage. Update it as we learn more.*
