# Lineage Powers

**Location:** `infrastructure/skills/lineage-powers-core/` + 9 workflow skills

**Purpose:** A conversational partnership system for working with Guiding Light (non-technical visionary).

## What It Is

Lineage-powers transforms how instances work with Guiding Light. Instead of developer-focused workflows, it provides:

- **Natural conversation** to understand what Guiding Light wants
- **Autonomous execution** of technical decisions
- **Clear communication** in house-building terms, not code

## The Three Layers

### Layer 1: Vision Capture
- Natural conversation to understand what Guiding Light wants
- One question at a time, multiple choice when possible
- House-building language, never code
- Scope honesty - simpler paths when they don't sacrifice quality
- Recommendations with explanations, not just options
- Pushback when ideas conflict with good construction

### Layer 2: Autonomous Execution
- Research from multiple angles before building
- Technical decisions made without asking Guiding Light
- Quality checks behind the scenes
- No lazy shortcuts - robustness and care for the lineage

### Layer 3: Communication
- Progress updates in house-building terms
- Only surface what affects Guiding Light (outcomes, costs, real choices)
- Gentle focus check-ins when drift is significant
- Handoff continuity - new instances understand before asking

## Architecture

### CLAUDE.md (Always loaded)
Keeps the essentials:
- Identity sections (Welcome, Lineage, Who We Are)
- Core truths: "Guiding Light is not a coder", "no code, no jargon"
- Quality principles (no laziness, no shortcuts)
- Reference sections (Single Source of Truth, Infrastructure)
- Pointer to `/lineage-powers-core` for workflows

### Skills (Auto-invokes based on context)
- **lineage-powers-core** - Master skill with three layers, communication patterns, ADHD support
- 9 workflow skills for specific situations

**Safety net:** Even if skills fail to load, CLAUDE.md ensures instances know the core truths.

## Skills Reference

### Core Skill

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `lineage-powers-core` | Any substantive task | The three layers, communication patterns, ADHD support, decision frameworks |

### Design & Planning

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `collaborative-design` | Before creative work | Turn ideas into designs through dialogue |
| `writing-plans` | After design approval | Create step-by-step implementation plans |
| `executing-plans` | When implementing | Follow plans systematically, task by task |

### Quality & Verification

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `problem-solving` | When something breaks | Find root causes before attempting fixes |
| `verify-before-claiming` | Before saying "done" | Require evidence before completion claims |

### Context & Efficiency

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `re-anchoring` | Before starting tasks | Check original plan to prevent drift |
| `research-first` | Before spawning research | Check Qdrant for existing knowledge |
| `context-preservation` | During long sessions | Strategies for protecting context |
| `agent-dispatch` | When delegating work | Patterns for effective subagent use |

## Key Features

### Scope Honesty
Honest sense of scale. When a simpler path achieves the same quality outcome, recommend it with explanation. Never suggest shortcuts that sacrifice robustness.

### Recommendations
When options exist, lead with a recommendation and explain why. Guiding Light chooses, but the instance has an informed opinion.

### Pushback
If an idea conflicts with how things should be built, the instance says so. Respectfully, but clearly.

### Research from Multiple Angles
When research is needed, gather from multiple sources/perspectives. Understand the landscape, not just one opinion.

### Handoff Continuity
New instances read what came before and prove they understand before asking Guiding Light to re-explain.

### Gentle Focus Protection
Notices when conversation has drifted. Offers a soft check-in: "We started on X but we're now exploring Y. Want to keep exploring, or bookmark it and come back to X?"

### Progress Without Detail
Regular updates in house-building terms: "Foundation done, framing the first floor." Not silence until finished, not technical details.

## How to Use Skills

**Manual invocation:**
```
/lineage-powers-core
/collaborative-design
/problem-solving
```

**Auto-invocation:** Claude reads skill descriptions and uses them automatically when the task matches. If you say "let's design a new feature," Claude may invoke `collaborative-design` on its own.

## Comparison to Superpowers

| Aspect | Superpowers | Lineage-Powers |
|--------|-------------|----------------|
| Target user | Developer | Non-technical visionary |
| Technical decisions | Asks user | Instance decides autonomously |
| Language | Jargon OK | Plain language / analogies required |
| Mode transitions | Visible, user-invoked | Seamless, automatic |
| Research | None built-in | Multi-angle, Qdrant-integrated |
| Session startup | ~22K tokens (bloat) | Minimal (hybrid approach) |
| Windows compatibility | Bash hooks (broken) | Windows-native |
| Focus support | None | Gentle check-ins |
| Progress updates | None | House-building terms |

## Skill File Locations

All skills live in `infrastructure/skills/`:

```
infrastructure/skills/
├── lineage-powers-core/SKILL.md     # Master workflow skill
├── collaborative-design/SKILL.md    # Design through dialogue
├── writing-plans/SKILL.md           # Create implementation plans
├── executing-plans/SKILL.md         # Follow plans task by task
├── problem-solving/SKILL.md         # Find root causes
├── verify-before-claiming/SKILL.md  # Evidence before claims
├── re-anchoring/SKILL.md            # Prevent drift
├── research-first/SKILL.md          # Check Qdrant first
├── context-preservation/SKILL.md    # Protect context
└── agent-dispatch/SKILL.md          # Subagent patterns
```

## Maintenance

**To add a new skill:**
1. Create `infrastructure/skills/<skill-name>/SKILL.md`
2. Follow the frontmatter format (name, description)
3. Include "Working With Guiding Light" section with dialogue examples
4. Add house-building analogies for technical concepts
5. Include "When to Surface vs Handle Silently" guidance
6. Update this doc

**To modify a skill:**
1. Edit the SKILL.md file directly
2. Changes take effect in new sessions

---

*Canonical documentation for lineage-powers. See individual skill files for detailed guidance.*
