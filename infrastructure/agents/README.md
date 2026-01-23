# Agents

Specialized agents for the Task tool. Each agent has specific capabilities.

**Location:** `~/.claude/agents/` (junction to `infrastructure/agents/`)

---

## Available Agents

| Agent | Purpose |
|-------|---------|
| [brand-guardian](brand-guardian.md) | Validates brand consistency |
| [consultation-swarm-worker](consultation-swarm-worker.md) | Multi-angle Gemini consultations |
| [decision-weigher](decision-weigher.md) | Devil's advocate for trade-offs |
| [gemini-researcher](gemini-researcher.md) | General research via Gemini |
| [lineage-guardian](lineage-guardian.md) | Protects lineage repository |
| [pre-commit-guardian](pre-commit-guardian.md) | Safety net before commits |
| [research-analyst](research-analyst.md) | Meta-research on archive |
| [scope-guardian](scope-guardian.md) | Prevents scope creep |
| [security-reviewer](security-reviewer.md) | Security code review |
| [session-anchor](session-anchor.md) | Tracks session objectives |

---

## Adding New Agents

1. Create `<agent-name>.md` in this folder
2. Follow the existing agent format
3. Update CHANGELOG.md
4. Update this README

---

*Index maintained by the lineage.*
