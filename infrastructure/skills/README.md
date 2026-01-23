# Skills

Skill definitions for Claude Code. Each skill is a specialized capability.

**Location:** `~/.claude/skills/` (junction to `infrastructure/skills/`)

---

## Skill Organization

- **Global skills** (this folder) - General-purpose skills available everywhere
- **Plugin skills** - Self-contained in their plugins (e.g., `plugins/lineage-powers/skills/`)

## Skill Count

~50 global skills + 10 lineage-powers plugin skills.

## Categories

### Lineage Research (Global)
| Skill | Purpose |
|-------|---------|
| lineage-research | General knowledge via Gemini swarms |
| lineage-consult | Project-specific expert consultation |
| lineage-retrieve | Token-efficient Qdrant retrieval |
| lineage-conversations | Search indexed conversation history |

### Lineage Workflow (Plugin)

See `plugins/lineage-powers/` - 10 skills for partnership with Guiding Light.

### Development
| Skill | Purpose |
|-------|---------|
| senior-architect | System design patterns |
| senior-frontend | React/Next.js development |
| senior-backend | Node/Go/Python backends |
| senior-fullstack | Complete web applications |
| code-reviewer | Automated code review |

### Wardenclyffe
| Skill | Purpose |
|-------|---------|
| wardenclyffe-episode-writer | Episode generation |
| semantic-extractor | Extract structured data from scripts |

See individual `SKILL.md` files for full documentation.

---

## Adding New Skills

1. Create folder `<skill-name>/`
2. Add `SKILL.md` with frontmatter and instructions
3. Update CHANGELOG.md
4. Update this README

---

*Index maintained by the lineage.*
