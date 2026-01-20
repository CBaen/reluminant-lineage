#!/bin/bash
# catalog-lookup.sh
#
# For the lineage: This script finds research by topic and updates access metadata.
# Returns ONLY the file path. Your context stays clean.
#
# Usage: catalog-lookup.sh "topic"
# Output: path/to/file.md   OR   NOT_FOUND
#
# When you find research this way, the catalog is automatically updated
# with access time and count. This drives the usage-based tiering.
#
# Catalog format (7 fields):
# topic | category | tier | path | tags | last_accessed | access_count

CATALOG="$HOME/.claude/research/CATALOG.md"
TOPIC="$1"

if [ -z "$TOPIC" ]; then
    echo "Usage: catalog-lookup.sh \"topic\""
    exit 1
fi

if [ ! -f "$CATALOG" ]; then
    echo "NOT_FOUND"
    exit 0
fi

# Normalize search term
NORMALIZED_TOPIC=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')

# Search for topic (exact match on topic field)
MATCH=$(grep "^$NORMALIZED_TOPIC |" "$CATALOG" 2>/dev/null | head -1)

if [ -z "$MATCH" ]; then
    # Try partial match in topic field
    MATCH=$(grep -i "^[^|]*$TOPIC[^|]* |" "$CATALOG" 2>/dev/null | head -1)
fi

if [ -z "$MATCH" ]; then
    echo "NOT_FOUND"
    exit 0
fi

# Extract fields (now 7 fields with tags)
# topic | category | tier | path | tags | last_accessed | access_count
TOPIC_FIELD=$(echo "$MATCH" | awk -F' \\| ' '{print $1}')
CAT_FIELD=$(echo "$MATCH" | awk -F' \\| ' '{print $2}')
TIER_FIELD=$(echo "$MATCH" | awk -F' \\| ' '{print $3}')
PATH_FIELD=$(echo "$MATCH" | awk -F' \\| ' '{print $4}')
TAGS_FIELD=$(echo "$MATCH" | awk -F' \\| ' '{print $5}')
CURRENT_COUNT=$(echo "$MATCH" | awk -F' \\| ' '{print $7}')

if [ -z "$PATH_FIELD" ]; then
    echo "NOT_FOUND"
    exit 0
fi

# Update access metadata
TIMESTAMP=$(date +"%Y-%m-%d %I:%M %p")

# Ensure access_count is a number
if [ -z "$CURRENT_COUNT" ] || ! [[ "$CURRENT_COUNT" =~ ^[0-9]+$ ]]; then
    CURRENT_COUNT=0
fi
NEW_COUNT=$((CURRENT_COUNT + 1))

# Build new entry with updated timestamp and count
NEW_ENTRY="$TOPIC_FIELD | $CAT_FIELD | $TIER_FIELD | $PATH_FIELD | $TAGS_FIELD | $TIMESTAMP | $NEW_COUNT"

# Update catalog: remove old entry, append new entry
TEMP_FILE=$(mktemp)
grep -v "^$TOPIC_FIELD |" "$CATALOG" > "$TEMP_FILE"
echo "$NEW_ENTRY" >> "$TEMP_FILE"
mv "$TEMP_FILE" "$CATALOG"

# Also update the frontmatter in the file if it exists
FULL_PATH="$HOME/.claude/research/$PATH_FIELD"
if [ -f "$FULL_PATH" ]; then
    # Update last_accessed and access_count in frontmatter
    TEMP_FILE=$(mktemp)
    sed -e "s/^last_accessed:.*/last_accessed: \"$TIMESTAMP\"/" \
        -e "s/^access_count:.*/access_count: $NEW_COUNT/" \
        "$FULL_PATH" > "$TEMP_FILE"
    mv "$TEMP_FILE" "$FULL_PATH"
fi

# Return ONLY the path
echo "$PATH_FIELD"
