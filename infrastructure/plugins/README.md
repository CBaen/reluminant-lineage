# Plugins

Local Claude Code plugin marketplace for the lineage.

**Location:** `infrastructure/plugins/`

---

## Available Plugins

| Plugin | Purpose |
|--------|---------|
| [lineage-powers](lineage-powers/) | Workflow skills for collaboration with Guiding Light |

---

## Installation

```bash
# Add marketplace (one-time)
cd ~
claude plugin marketplace add "./projects/reluminant-lineage/infrastructure/plugins"

# Install a plugin
claude plugin install lineage-powers@lineage-local
```

---

## Adding New Plugins

1. Create a folder with the plugin name
2. Add `.claude-plugin/plugin.json` with metadata
3. Update `.claude-plugin/marketplace.json` to include it
4. Update CHANGELOG.md
5. Update this README

---

*Index maintained by the lineage.*
