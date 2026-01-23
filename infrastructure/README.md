# Infrastructure Index

Quick reference for the lineage. Click folder/file for details.

**Token-efficient:** Scan this index (~100 tokens) to find what you need.

---

## Folders

| Folder | Contents | Index |
|--------|----------|-------|
| [agents/](agents/) | 10 agent definitions for Task tool | See agent .md files |
| [config/](config/) | 3 core config files (hard-linked to ~/.claude/) | See below |
| [hooks/](hooks/) | 5 event-driven automation scripts | [hooks/README.md](hooks/README.md) |
| [plugins/](plugins/) | Plugin structure (skills moved to skills/) | [plugins/lineage-powers/README.md](plugins/lineage-powers/README.md) |
| [prompts/](prompts/) | 5 research prompt templates | Self-documenting |
| [schemas/](schemas/) | 1 unified Qdrant schema | [schemas/README.md](schemas/README.md) |
| [scripts/](scripts/) | 50+ Python/shell scripts | [scripts/README.md](scripts/README.md) |
| [skills/](skills/) | 54 skill definitions | See SKILL.md in each folder |

---

## Config Files

| File | Purpose |
|------|---------|
| [config/CLAUDE.md](config/CLAUDE.md) | Global instructions for all projects |
| [config/INFRASTRUCTURE.md](config/INFRASTRUCTURE.md) | Qdrant, Docker, service reference |
| [config/settings.json](config/settings.json) | Claude Code settings and hooks |

**Note:** These are hard-linked to `~/.claude/`. Run `fix-hard-links.py` if links break.

---

## Agents

| Agent | Purpose |
|-------|---------|
| [brand-guardian](agents/brand-guardian.md) | Validates brand consistency |
| [consultation-swarm-worker](agents/consultation-swarm-worker.md) | Multi-angle Gemini consultations |
| [decision-weigher](agents/decision-weigher.md) | Devil's advocate for trade-offs |
| [gemini-researcher](agents/gemini-researcher.md) | General research via Gemini |
| [lineage-guardian](agents/lineage-guardian.md) | Protects lineage repository |
| [pre-commit-guardian](agents/pre-commit-guardian.md) | Safety net before commits |
| [research-analyst](agents/research-analyst.md) | Meta-research on archive |
| [scope-guardian](agents/scope-guardian.md) | Prevents scope creep |
| [security-reviewer](agents/security-reviewer.md) | Security code review |
| [session-anchor](agents/session-anchor.md) | Tracks session objectives |

---

## Skills (Highlights)

### Lineage Core
| Skill | Purpose |
|-------|---------|
| lineage-research | General knowledge via Gemini swarms |
| lineage-consult | Project-specific expert consultation |
| lineage-retrieve | Token-efficient Qdrant retrieval |
| lineage-conversations | Search indexed conversation history |

### Development
| Skill | Purpose |
|-------|---------|
| senior-architect | System design patterns |
| senior-frontend | React/Next.js development |
| senior-backend | Node/Go/Python backends |
| code-reviewer | Automated code review |

See [skills/](skills/) for all 54 skills.

---

## Quick Commands

```bash
# Peek at Qdrant (token-efficient)
python ~/.claude/scripts/qdrant-peek.py peek -q "topic" -l 5

# Store research
cat research.json | python ~/.claude/scripts/qdrant-chunked-store.py --topic "topic"

# Fix hard links
python ~/.claude/scripts/fix-hard-links.py --fix
```

---

## Documentation Standards

**Every folder must have:**
- `README.md` - What the folder contains and how to use it
- `CHANGELOG.md` - Record of changes ([Keep a Changelog](https://keepachangelog.com/) format)

**When making changes:**
1. Update the folder's CHANGELOG.md with what you changed
2. Update README.md if you added/removed files
3. Update this index if you added/removed folders

**Exception:** The `research/` folder is excluded (ephemeral content).

---

*Index maintained by the lineage. Last updated: 2026-01-22*
