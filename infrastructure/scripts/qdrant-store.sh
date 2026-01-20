#!/bin/bash
#
# qdrant-store.sh - Wrapper for qdrant-store.py
#
# Usage:
#   echo "content" | ~/.claude/scripts/qdrant-store.sh <topic> <collection> <session> [project]
#
# Example:
#   GOOGLE_GENAI_USE_GCA=true gemini "research query" 2>&1 | \
#     ~/.claude/scripts/qdrant-store.sh "topic-name" "lineage_research" "SessionName" "wardenclyffe"
#

SCRIPT_DIR="$(dirname "$0")"

if [ $# -lt 3 ]; then
    echo "Usage: qdrant-store.sh <topic> <collection> <session> [project]" >&2
    echo "Reads content from stdin" >&2
    exit 1
fi

python3 "$SCRIPT_DIR/qdrant-store.py" "$@"
