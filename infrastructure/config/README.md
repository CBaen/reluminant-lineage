# Config

Core configuration files for Claude Code. These are hard-linked to `~/.claude/`.

**Location:** Hard-linked to `~/.claude/`

---

## Files

| File | Purpose |
|------|---------|
| [CLAUDE.md](CLAUDE.md) | Global instructions for all projects |
| [INFRASTRUCTURE.md](INFRASTRUCTURE.md) | Qdrant, Docker, service reference |
| [settings.json](settings.json) | Claude Code settings and hooks |

---

## Hard Links

These files are hard-linked between here and `~/.claude/`. This means:
- Editing either location updates both (same file, two paths)
- Links can break if files are replaced instead of edited

**To check/fix links:**
```bash
python ~/.claude/scripts/fix-hard-links.py        # Check status
python ~/.claude/scripts/fix-hard-links.py --fix  # Fix if broken
```

---

## Making Changes

1. Edit the file (either location works)
2. Run `fix-hard-links.py` to verify links are intact
3. Update CHANGELOG.md
4. Commit and push

---

*Index maintained by the lineage.*
