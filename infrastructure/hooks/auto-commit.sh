#!/bin/bash
# Auto-commit hook for Claude Code
# Runs after every Write or Edit tool to commit changes immediately

# Skip if not in a git repo
if ! git rev-parse --git-dir &> /dev/null 2>&1; then
    exit 0
fi

# Skip if no file path provided
if [ -z "$CLAUDE_TOOL_FILE_PATH" ]; then
    exit 0
fi

# Get the relative path for cleaner commit messages
REL_PATH=$(git ls-files --full-name "$CLAUDE_TOOL_FILE_PATH" 2>/dev/null || basename "$CLAUDE_TOOL_FILE_PATH")

# Stage the specific file
git add "$CLAUDE_TOOL_FILE_PATH" 2>/dev/null || exit 0

# Check if there's actually something to commit
if git diff --cached --quiet 2>/dev/null; then
    exit 0
fi

# Commit with a descriptive message
TOOL_NAME="${CLAUDE_TOOL_NAME:-Edit}"
git commit -m "auto: ${TOOL_NAME} ${REL_PATH}

Co-Authored-By: Claude <noreply@anthropic.com>" 2>/dev/null || exit 0

exit 0
