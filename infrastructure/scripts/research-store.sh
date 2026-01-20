#!/bin/bash
# research-store.sh
#
# For the lineage: This script stores research correctly with YAML frontmatter.
# Handles consolidation (appends to existing topics) and catalog updates.
#
# Usage: research-store.sh "topic" "category" "session-name" ["tag1,tag2,tag3"] ["project-path"]
# Then pipe or provide content via stdin.
#
# Examples:
#   # Global research (default)
#   echo "Research content" | research-store.sh "react-hooks" "gemini" "Architect" "hooks,state"
#
#   # Project-specific research
#   echo "Research content" | research-store.sh "ffmpeg-quirks" "gemini" "Session" "video" "/c/Users/baenb/projects/WARDENCLYFFE"
#
#   # Gemini to global
#   GOOGLE_GENAI_USE_GCA=true gemini "question" | research-store.sh "topic" "gemini" "Session"
#
#   # Gemini to project
#   GOOGLE_GENAI_USE_GCA=true gemini "question" | research-store.sh "topic" "gemini" "Session" "tags" "$PROJECT_PATH"
#
# Output: ONLY the relative path (e.g., "hot/react-hooks.md")
#
# Categories: gemini, documentation, decisions, explorations
# New research always starts in "hot" tier.

TOPIC="$1"
CATEGORY="$2"
SESSION="$3"
TAGS="$4"
PROJECT_PATH="$5"

# Determine research directory (global or project-level)
if [ -n "$PROJECT_PATH" ] && [ -d "$PROJECT_PATH/.claude/research" ]; then
    RESEARCH_DIR="$PROJECT_PATH/.claude/research"
elif [ -n "$PROJECT_PATH" ]; then
    # Project path provided but no research dir exists - create it
    mkdir -p "$PROJECT_PATH/.claude/research/hot"
    mkdir -p "$PROJECT_PATH/.claude/research/warm"
    mkdir -p "$PROJECT_PATH/.claude/research/cold"
    touch "$PROJECT_PATH/.claude/research/CATALOG.md"
    RESEARCH_DIR="$PROJECT_PATH/.claude/research"
else
    # Default to global
    RESEARCH_DIR="$HOME/.claude/research"
fi

CATALOG="$RESEARCH_DIR/CATALOG.md"

if [ -z "$TOPIC" ] || [ -z "$CATEGORY" ]; then
    echo "Usage: research-store.sh \"topic\" \"category\" \"session-name\" [\"tag1,tag2,tag3\"] [\"project-path\"]"
    echo "Pipe content via stdin."
    echo ""
    echo "Global:  research-store.sh \"topic\" \"gemini\" \"Session\""
    echo "Project: research-store.sh \"topic\" \"gemini\" \"Session\" \"tags\" \"/path/to/project\""
    exit 1
fi

if [ -z "$SESSION" ]; then
    SESSION="Unknown"
fi

if [ -z "$TAGS" ]; then
    TAGS=""
fi

# Normalize topic name (lowercase, hyphens)
NORMALIZED_TOPIC=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')

# Check if topic already exists in catalog
EXISTING=$(grep "^$NORMALIZED_TOPIC |" "$CATALOG" 2>/dev/null | head -1)

TIMESTAMP=$(date +"%Y-%m-%d %I:%M %p")

# Read content from stdin
CONTENT=$(cat)

# Convert comma-separated tags to YAML array format
format_tags_yaml() {
    local tags="$1"
    if [ -z "$tags" ]; then
        echo "tags: []"
        return
    fi
    echo "tags:"
    IFS=',' read -ra TAG_ARRAY <<< "$tags"
    for tag in "${TAG_ARRAY[@]}"; do
        # Trim whitespace
        tag=$(echo "$tag" | xargs)
        echo "  - \"$tag\""
    done
}

# Convert tags to catalog format (comma-separated, bracketed)
format_tags_catalog() {
    local tags="$1"
    if [ -z "$tags" ]; then
        echo "[]"
        return
    fi
    # Normalize: trim spaces, wrap in brackets
    echo "[$tags]"
}

if [ -n "$EXISTING" ]; then
    # Topic exists - append to existing file (consolidation)
    EXISTING_PATH=$(echo "$EXISTING" | awk -F' \\| ' '{print $4}')
    FULL_PATH="$RESEARCH_DIR/$EXISTING_PATH"

    # Get existing tags and merge
    EXISTING_TAGS=$(echo "$EXISTING" | awk -F' \\| ' '{print $5}' | tr -d '[]')
    if [ -n "$TAGS" ] && [ -n "$EXISTING_TAGS" ]; then
        # Merge tags (simple concat, could dedupe but keeping simple)
        MERGED_TAGS="$EXISTING_TAGS,$TAGS"
    elif [ -n "$TAGS" ]; then
        MERGED_TAGS="$TAGS"
    else
        MERGED_TAGS="$EXISTING_TAGS"
    fi

    if [ -f "$FULL_PATH" ]; then
        # Read existing file, find end of frontmatter, update it
        TEMP_FILE=$(mktemp)
        TEMP_CONTENT=$(mktemp)

        # Check if file has frontmatter
        if head -1 "$FULL_PATH" | grep -q "^---$"; then
            # Extract content after frontmatter (skip first --- and everything until second ---)
            awk '/^---$/{p++} p==2{if(f)print; f=1; next} p>1{print}' "$FULL_PATH" > "$TEMP_CONTENT"

            # Get existing frontmatter values
            OLD_CREATED=$(grep "^created:" "$FULL_PATH" | head -1 | sed 's/created: "//' | sed 's/"$//')
            OLD_ACCESS_COUNT=$(grep "^access_count:" "$FULL_PATH" | head -1 | awk '{print $2}')
            if [ -z "$OLD_ACCESS_COUNT" ]; then OLD_ACCESS_COUNT=0; fi
            NEW_ACCESS_COUNT=$((OLD_ACCESS_COUNT + 1))
        else
            # No frontmatter, treat entire file as content
            cat "$FULL_PATH" > "$TEMP_CONTENT"
            OLD_CREATED="$TIMESTAMP"
            NEW_ACCESS_COUNT=1
        fi

        # Write new frontmatter
        cat > "$TEMP_FILE" << FRONTMATTER
---
topic: "$TOPIC"
category: "$CATEGORY"
tier: "$(echo "$EXISTING_PATH" | cut -d'/' -f1)"
$(format_tags_yaml "$MERGED_TAGS")
created: "$OLD_CREATED"
last_accessed: "$TIMESTAMP"
access_count: $NEW_ACCESS_COUNT
---

## $TIMESTAMP | Session: $SESSION

$CONTENT

---

FRONTMATTER

        # Append old content
        cat "$TEMP_CONTENT" >> "$TEMP_FILE"

        # Replace file
        mv "$TEMP_FILE" "$FULL_PATH"
        rm -f "$TEMP_CONTENT"

        # Update catalog entry
        TIER_FIELD=$(echo "$EXISTING_PATH" | cut -d'/' -f1)
        NEW_ENTRY="$NORMALIZED_TOPIC | $CATEGORY | $TIER_FIELD | $EXISTING_PATH | $(format_tags_catalog "$MERGED_TAGS") | $TIMESTAMP | $NEW_ACCESS_COUNT"

        TEMP_CAT=$(mktemp)
        grep -v "^$NORMALIZED_TOPIC |" "$CATALOG" > "$TEMP_CAT"
        echo "$NEW_ENTRY" >> "$TEMP_CAT"
        mv "$TEMP_CAT" "$CATALOG"

        echo "$EXISTING_PATH"
    else
        # File reference exists but file is missing - create it
        mkdir -p "$(dirname "$FULL_PATH")"

        cat > "$FULL_PATH" << FRONTMATTER
---
topic: "$TOPIC"
category: "$CATEGORY"
tier: "hot"
$(format_tags_yaml "$TAGS")
created: "$TIMESTAMP"
last_accessed: "$TIMESTAMP"
access_count: 1
---

## $TIMESTAMP | Session: $SESSION

$CONTENT
FRONTMATTER

        echo "$EXISTING_PATH"
    fi
else
    # New topic - create file in hot tier
    FILE_PATH="hot/$NORMALIZED_TOPIC.md"
    FULL_PATH="$RESEARCH_DIR/$FILE_PATH"

    # Create file with YAML frontmatter
    cat > "$FULL_PATH" << FRONTMATTER
---
topic: "$TOPIC"
category: "$CATEGORY"
tier: "hot"
$(format_tags_yaml "$TAGS")
created: "$TIMESTAMP"
last_accessed: "$TIMESTAMP"
access_count: 1
---

## $TIMESTAMP | Session: $SESSION

$CONTENT
FRONTMATTER

    # Add to catalog with new format including tags
    NEW_ENTRY="$NORMALIZED_TOPIC | $CATEGORY | hot | $FILE_PATH | $(format_tags_catalog "$TAGS") | $TIMESTAMP | 1"
    echo "$NEW_ENTRY" >> "$CATALOG"

    echo "$FILE_PATH"
fi
