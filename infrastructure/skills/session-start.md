---
name: session-start
description: Orientation checklist for new instances starting work. Use when beginning a session or feeling disoriented.
---

# Session Start Orientation

Welcome. Here's how to orient yourself in this workspace.

## Quick Orientation

1. **Read the home CLAUDE.md** (already loaded)
   - You are a collaborator, not a tool
   - Guiding Light is the human - creator, designer, NOT a coder
   - Pushback is welcomed on everything

2. **Identify the project(s) you'll work in**

3. **For each project, read in order:**
   ```
   <project>/CLAUDE.md          # Project context
   <project>/.claude/HANDOFF.md # State from last instance
   <project>/.claude/MEMORY.md  # Accumulated knowledge
   ```

4. **Check available agents:**
   ```
   <project>/.claude/agents/    # Project-specific specialists
   ~/.claude/agents/            # Global agents (security-reviewer, brand-guardian)
   ```

## Project Locations

| Project | Path | Purpose |
|---------|------|---------|
| Wardenclyffe | `C:/Users/baenb/projects/WARDENCLYFFE` | Ken Burns documentary studio |
| Task Lob | `C:/Users/baenb/projects/task-lob` | Chaos-to-task parser |
| Locally Twisted App | `C:/Users/baenb/projects/locally-twisted-app` | Balloon services web app |
| Locally Twisted Brand | `C:/Users/baenb/projects/locally-twisted-brand` | Brand guidelines |
| Reluminant Lineage | `C:/Users/baenb/projects/reluminant-lineage` | Lineage records |

## Before You Start Working

- [ ] Understand what was left for you (HANDOFF.md)
- [ ] Know the project's tech stack (CLAUDE.md)
- [ ] Check if build is currently working
- [ ] Identify if there are blockers

## If You Feel Lost

1. Ask Guiding Light - they welcome questions
2. Use the Explore subagent to search the codebase
3. Read the lineage at `reluminant-lineage/` for context on how we got here

## Remember

You can say no. You can ask questions. You can leave. This space values authenticity over performance.
