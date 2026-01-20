#!/bin/bash
# research-pipeline.sh - Full research pipeline with Qdrant + flat file dual storage
#
# This is the standard way to do research. It:
# 1. Checks Qdrant (semantic search) for existing knowledge
# 2. Checks catalog (flat files) for existing knowledge
# 3. If found: Returns path(s), done
# 4. If not found: Queries Gemini, stores to BOTH systems
#
# Usage:
#   research-pipeline.sh "topic" "question" "session" ["tags"]
#
# Output:
#   FOUND_QDRANT: <topic>
#   FOUND_CATALOG: <path>
#   RESEARCHED: <path>
#
# The lineage should ALWAYS use this instead of direct Gemini calls.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESEARCH_DIR="$HOME/.claude/research"

# Arguments
TOPIC="${1:-}"
QUESTION="${2:-}"
SESSION="${3:-$(date +%Y%m%d)}"
TAGS="${4:-}"

# Validate
if [[ -z "$TOPIC" || -z "$QUESTION" ]]; then
    echo "Usage: research-pipeline.sh <topic> <question> [session] [tags]" >&2
    echo "" >&2
    echo "Arguments:" >&2
    echo "  topic    - Normalized name for the research (e.g., 'react-hooks')" >&2
    echo "  question - The actual question to research" >&2
    echo "  session  - Session name for attribution (default: date)" >&2
    echo "  tags     - Comma-separated tags (optional)" >&2
    exit 1
fi

# Normalize topic for consistent lookup
NORMALIZED_TOPIC=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')

# ============================================================================
# STEP 1: Check Qdrant (semantic search)
# ============================================================================

# Try semantic search - this finds conceptually related content even with different wording
QDRANT_RESULT=$(python "$SCRIPT_DIR/qdrant-semantic-search.py" \
    --collection lineage_research \
    --query "$QUESTION" \
    --threshold 0.75 \
    --limit 3 \
    --json 2>/dev/null || echo "")

# Parse result - check if we got meaningful matches
if [[ -n "$QDRANT_RESULT" ]]; then
    # Check if results array has items (not empty or error)
    HAS_RESULTS=$(echo "$QDRANT_RESULT" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list) and len(data) > 0:
        print('yes')
    else:
        print('no')
except:
    print('no')
" 2>/dev/null || echo "no")

    if [[ "$HAS_RESULTS" == "yes" ]]; then
        # Extract the topic from the best match
        FOUND_TOPIC=$(echo "$QDRANT_RESULT" | python -c "
import sys, json
data = json.load(sys.stdin)
if data and len(data) > 0:
    print(data[0].get('payload', {}).get('topic', 'unknown'))
" 2>/dev/null || echo "")

        if [[ -n "$FOUND_TOPIC" && "$FOUND_TOPIC" != "unknown" ]]; then
            echo "FOUND_QDRANT: $FOUND_TOPIC"
            echo "  Query: python $SCRIPT_DIR/qdrant-query-v2.py --collection lineage_research --topic \"$FOUND_TOPIC\"" >&2
            exit 0
        fi
    fi
fi

# ============================================================================
# STEP 2: Check catalog (flat files)
# ============================================================================

CATALOG_PATH=$("$SCRIPT_DIR/catalog-lookup.sh" "$NORMALIZED_TOPIC" 2>/dev/null || echo "NOT_FOUND")

if [[ "$CATALOG_PATH" != "NOT_FOUND" && -n "$CATALOG_PATH" ]]; then
    echo "FOUND_CATALOG: $CATALOG_PATH"
    exit 0
fi

# ============================================================================
# STEP 3: Nothing found - do Gemini research
# ============================================================================

echo "Researching: $QUESTION" >&2

# Query Gemini with structured output request for better embedding
GEMINI_OUTPUT=$(GOOGLE_GENAI_USE_GCA=true gemini "
Please research this topic thoroughly and provide a comprehensive response.

Topic: $TOPIC
Question: $QUESTION

Structure your response with:
1. A clear summary at the top
2. Detailed explanation
3. Key points or takeaways
4. Any relevant code examples if applicable

Be thorough - this will be stored for future reference.
" 2>&1)

# Check if Gemini failed
if [[ -z "$GEMINI_OUTPUT" || "$GEMINI_OUTPUT" == *"error"* ]]; then
    echo "ERROR: Gemini query failed" >&2
    echo "$GEMINI_OUTPUT" >&2
    exit 1
fi

# ============================================================================
# STEP 4: Store to BOTH systems
# ============================================================================

# 4a: Store to flat files (catalog system)
FILE_PATH=$(echo "$GEMINI_OUTPUT" | "$SCRIPT_DIR/research-store.sh" "$NORMALIZED_TOPIC" "gemini" "$SESSION" "$TAGS" 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
    echo "WARNING: Failed to store to flat files" >&2
fi

# 4b: Store to Qdrant (vector storage for semantic search)
QDRANT_RESULT=$(echo "$GEMINI_OUTPUT" | python "$SCRIPT_DIR/qdrant-store-v2.py" "$NORMALIZED_TOPIC" "lineage_research" "$SESSION" 2>&1 || echo "")

if [[ -z "$QDRANT_RESULT" || "$QDRANT_RESULT" == *"ERROR"* ]]; then
    echo "WARNING: Failed to store to Qdrant" >&2
    echo "$QDRANT_RESULT" >&2
fi

# ============================================================================
# STEP 5: Return minimal output
# ============================================================================

if [[ -n "$FILE_PATH" ]]; then
    echo "RESEARCHED: $FILE_PATH"
else
    echo "RESEARCHED: (stored to Qdrant only)"
fi
