---
name: lineage-consult
description: Expert consultative research via Gemini swarms. Implementation-focused guidance with project context.
allowed-tools: Task, TodoWrite, Bash, Read
---

# Lineage Consult Skill

**PURPOSE:** Get implementation-focused guidance specific to YOUR context - your tech stack, your constraints, your goals.

For general "what is X" questions, use `lineage-research` instead.

---

## When to Use

- "How should OUR React/Express/JWT stack handle token refresh?"
- "Given our Qdrant setup, what's the best way to implement status tracking?"
- "What architecture should we use for our specific use case?"

## When NOT to Use

- "What is OAuth?" → use `lineage-research`
- General knowledge questions → use `lineage-research`
- Simple questions you can answer directly → just answer

---

## The Core Difference: Hyperspecificity

**This is the ONLY difference between lineage-consult and lineage-research.**

| lineage-research | lineage-consult |
|------------------|-----------------|
| "What are Windows IPC options?" | "For OUR stack (Git Bash + Python on Windows 11), what's the BEST IPC method?" |
| Generic theory and best practices | Exact code modifications for OUR scripts |
| Works for anyone | Works ONLY for us |

### What to Include in Every Consultation

| Category | Example |
|----------|---------|
| **Exact OS** | Windows 11 Pro, Git Bash (MINGW64) |
| **Exact scripts** | Paste relevant code from `~/.claude/scripts/` |
| **Exact services** | Qdrant localhost:6333, Ollama localhost:11434 |
| **Exact constraints** | 4GB VRAM, 2 Gemini accounts, 60 RPM limit |
| **Exact problem** | "Output truncates at 32KB" not "output is unreliable" |
| **Desired outcome** | "Give us modified code" not "explain how to fix" |

**If Gemini's response could apply to anyone, the consultation was too generic. Redo it.**

---

## Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `{{TOPIC}}` | Yes | - | What to consult on |
| `{{PROJECT_CONTEXT}}` | Yes | - | Your stack, constraints, current code |
| `{{DATE}}` | No | auto-generated | Current date (YYYY-MM-DD) - forces Gemini live search |
| `{{COLLECTION}}` | No | `universal_vault` | Qdrant collection (2026 migration) |
| `{{SESSION}}` | No | auto-generated | Format: `[project]-consult-[YYYY-MM-DD]` |

**Note (2026 Migration):** Consultations are stored to `universal_vault` using `--hybrid` flag. Query using `--hybrid` for best results.

---

## System Context

Every consultation should include your system context:

```
SYSTEM CONTEXT:
- Hardware: i7-11850H, 48GB RAM, NVIDIA T600 (4GB VRAM)
- Embedding: Ollama nomic-embed-text (parallel: 32 in ~2.4s)
- Vector DB: Qdrant localhost:6333
- AI: Claude Code (Opus 4.5), Gemini (2 accounts)
- OS: Windows 11 with Git Bash
- Constraints: 4GB VRAM, laptop thermals

CHALLENGE OUR CHOICES: Question if this tech stack is optimal.
```

---

## How to Use

**STEP 1: Create todo**

```
TodoWrite:
  - content: "Consult on [TOPIC] via Gemini swarm"
    status: "in_progress"
    activeForm: "Getting expert consultation on [TOPIC]"
```

**STEP 2: Spawn the swarm worker**

```
Task tool:
  subagent_type: "general-purpose"
  model: "sonnet"
  prompt: |
    Read ~/.claude/agents/consultation-swarm-worker.md for your full instructions.

    TOPIC: [your topic]
    PROJECT_CONTEXT: [your stack, constraints, current code]
    COLLECTION: [qdrant collection]
    SESSION: [session name]
    DATE: [current date YYYY-MM-DD]

    Execute the workflow in that file.
```

**STEP 3: Receive coordinates**

The subagent returns ONLY:
- Session ID and collection name
- Point IDs stored
- Success/failure counts
- Primary recommendation (one sentence)

You do NOT receive the consultation content - it's in Qdrant.

**STEP 4: Retrieve if needed**

```bash
python ~/.claude/scripts/qdrant-semantic-search.py --collection [collection] --query "[topic]" --limit 5
```

---

## Consultation Angles

The subagent runs minimum 5 angles:

| Angle | Questions It Answers |
|-------|---------------------|
| Problem Analysis | What's the actual problem? Current vs desired state? |
| Architecture Options | What approaches fit THIS stack? Trade-offs? |
| Implementation Details | Specific code patterns, APIs, configurations? |
| Security & Risks | Vulnerabilities? Edge cases? What could go wrong? |
| Validation & Testing | How to verify it works? Test strategies? |

---

## What You Get Back

The subagent stores to Qdrant:
- 5+ research sessions (one per angle)
- 8+ chunks per session (40+ total chunks)
- Implementation plans with phases and tasks
- Action items tied to YOUR context

You get coordinates to retrieve what you need.

---

## Remember

This skill is for EXPERT CONSULTATION, not information retrieval.

**The test:** If Gemini's response could apply to any project, the consultation failed. It should ONLY work for us.

**Include our code.** Include our constraints. Include our exact problem.
