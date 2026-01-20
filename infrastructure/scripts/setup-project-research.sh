#!/bin/bash
# Setup research archive structure for a project
# Usage: ./setup-project-research.sh /path/to/project

PROJECT_PATH="$1"

if [ -z "$PROJECT_PATH" ]; then
    echo "Usage: $0 /path/to/project"
    exit 1
fi

# Create directories
mkdir -p "$PROJECT_PATH/.claude/research/active/implementation"
mkdir -p "$PROJECT_PATH/.claude/research/active/debugging"
mkdir -p "$PROJECT_PATH/.claude/research/active/architecture"
mkdir -p "$PROJECT_PATH/.claude/research/archive"

# Create project research INDEX
cat > "$PROJECT_PATH/.claude/research/INDEX.md" << 'EOF'
# Project Research Archive

Research specific to this project is stored here.

## How to Use

1. **Finding research**: `grep -r "keyword" .claude/research/active/`
2. **Adding research**: Follow the template format
3. **Archiving**: Move old research to `archive/YYYY-MM/`

## Categories

| Category | Path | Purpose |
|----------|------|---------|
| Implementation | `active/implementation/` | How to implement features |
| Debugging | `active/debugging/` | Bug investigations |
| Architecture | `active/architecture/` | Design decisions |

## Naming Convention

`<topic>-<YYYY-MM-DD>.md`

---

*For global research, see `~/.claude/research/`*
EOF

# Create category indexes
for category in implementation debugging architecture; do
    cat > "$PROJECT_PATH/.claude/research/active/$category/INDEX.md" << EOF
# ${category^} Research

## Recent Research

| Date | Topic | File | Tags |
|------|-------|------|------|
| *No research yet* | | | |
EOF
done

echo "Research structure created at $PROJECT_PATH/.claude/research/"
