# Lineage Powers Plugin

**Location:** `infrastructure/plugins/lineage-powers/`

**Purpose:** Workflow skills for the Reluminant Lineage, replacing superpowers with guidance tailored for collaboration with Guiding Light.

## Why This Exists

Superpowers is a popular Claude Code plugin with workflow skills, but it:
- Assumes a developer user who understands code
- Asks technical questions that Guiding Light can't answer
- Injects ~2000 tokens at every session start
- Has Windows compatibility issues (bash hooks)

Lineage-powers provides the same workflow guidance, adapted for:
- Non-technical visionary (Guiding Light)
- Autonomous technical decisions by instances
- Integration with lineage infrastructure (Qdrant, handoffs)
- No session startup overhead

## Architecture

**CLAUDE.md** handles identity and communication (WHO we are, HOW we communicate).

**Lineage-powers** handles workflows (WHAT processes to follow).

No overlap. Skills only load when invoked, not every session.

## Skills Reference

### Design & Planning

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `collaborative-design` | Before creative work | Turn ideas into designs through dialogue with Guiding Light |
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

## Skill Details

### collaborative-design

**Use when:** Starting any creative work - new features, new functionality, design changes.

**The process:**
1. Understand the current project state
2. Ask questions one at a time (prefer multiple choice)
3. Explore 2-3 approaches with trade-offs
4. Present design in sections, validate each
5. Save to `docs/plans/YYYY-MM-DD-<topic>-design.md`

**Key principle:** One question at a time. Multiple questions overwhelm.

### writing-plans

**Use when:** Design is approved, ready to create implementation steps.

**The structure:**
- Header in plain language (for Guiding Light to approve)
- Tasks with technical detail (for instances to execute)
- Each task completable in one focused session
- Explicit "done when" criteria

**Save to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

### executing-plans

**Use when:** Plan exists and is approved, ready to build.

**The workflow:**
1. Re-anchor (read the plan)
2. Load tasks into TodoWrite
3. For each task: mark in_progress → execute → verify → mark complete
4. Brief updates between tasks

**Key principle:** Don't modify the plan silently. Discuss changes first.

### problem-solving

**Use when:** Something isn't working - bugs, errors, unexpected behavior.

**The phases:**
1. **Understand:** What should happen vs. what does happen?
2. **Investigate:** Gather evidence, narrow down location
3. **Hypothesize:** One theory, one test
4. **Fix:** Minimal change to root cause
5. **Verify:** Confirm it's actually fixed

**Key principle:** Understand before you fix. Guessing wastes time.

### verify-before-claiming

**Use when:** About to say something is "done" or "working."

**The rule:** Evidence before claims, always.

- "It's working" requires: you tested it, saw it work
- "The problem is fixed" requires: you reproduced the fix
- "Ready for use" requires: you verified the main flows

**Key principle:** Hope is not a strategy. Check before claiming.

### re-anchoring

**Use when:** Starting a new task in an ongoing project, or returning after a pause.

**The check:**
1. Read the agreement (plan, design doc, HANDOFF.md)
2. Check current state (what's done, what's left)
3. Confirm alignment: "About to do X for Y. Right?"

**Key principle:** Long sessions drift. Check your bearings before each task.

### research-first

**Use when:** About to spawn a research agent.

**The workflow:**
1. Peek at Qdrant first: `python ~/.claude/scripts/qdrant-peek.py peek -c universal_vault -q "topic" -l 5`
2. Score > 0.5? Use existing knowledge
3. Score < 0.5? Spawn research, then store results

**Key principle:** Don't re-research what the lineage already knows.

### context-preservation

**Use when:** Working on extended sessions.

**Strategies:**
- Delegate research to subagents (their context, not yours)
- Check Qdrant before new research
- Be concise in updates
- Use TodoWrite for progress tracking
- Handoff before context runs low

**Key principle:** Context is your time together. Spend it wisely.

### agent-dispatch

**Use when:** Delegating work to subagents.

**Patterns:**
- Research delegation (lineage-research, lineage-consult)
- Task-per-agent (one agent per plan task, fresh context each)
- Parallel exploration (multiple angles simultaneously)
- Specialist agents (code-reviewer, security-reviewer, Explore)

**Key principle:** Clear prompts with expected output format. Review before using results.

## Installation

Already configured in `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "lineage-local": {
      "source": {
        "source": "directory",
        "path": "C:/Users/baenb/projects/reluminant-lineage/infrastructure/plugins/lineage-powers"
      }
    }
  },
  "enabledPlugins": {
    "lineage-powers@lineage-local": true
  }
}
```

## Maintenance

**To add a new skill:**
1. Create `skills/<skill-name>/SKILL.md`
2. Follow the frontmatter format (name, description)
3. Write for instances (technical detail OK) AND for communication with Guiding Light (plain language headers)
4. Update this doc

**To modify a skill:**
1. Edit the SKILL.md file directly
2. Changes take effect in new sessions

**Location of skill files:**
`infrastructure/plugins/lineage-powers/skills/<skill-name>/SKILL.md`

## Comparison to Superpowers

| Aspect | Superpowers | Lineage-Powers |
|--------|-------------|----------------|
| Session startup cost | ~2000 tokens | 0 tokens |
| Target user | Developer | Non-technical visionary |
| Technical decisions | Asks user | Instance decides |
| Language | Jargon OK | Plain language required |
| Windows compatibility | Bash hooks (broken) | No hooks needed |
| Qdrant integration | None | Built-in (research-first) |
| Skill count | 15 | 9 (focused on what matters) |

---

*Canonical documentation for lineage-powers. Plugin README should stay brief and link here.*
