#!/bin/bash
# research-rotate.sh
#
# For the lineage: This script handles usage-based tier rotation.
# Run periodically (session start/end) to keep tiers accurate.
#
# Usage: research-rotate.sh [--dry-run]
#
# Rotation rules (usage-based, not time-based):
#
# DEMOTION (inactivity):
#   - hot → warm: No access for 14+ days
#   - warm → cold: No access for 21+ days
#
# PROMOTION (active use):
#   - cold → warm: Accessed in last 7 days AND access_count >= 3
#   - warm → hot: Accessed in last 3 days AND access_count >= 5
#
# Files are never deleted. Cold is the floor, not oblivion.

RESEARCH_DIR="$HOME/.claude/research"
CATALOG="$RESEARCH_DIR/CATALOG.md"
DRY_RUN=false

if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "DRY RUN - no changes will be made"
    echo ""
fi

if [ ! -f "$CATALOG" ]; then
    echo "No catalog found at $CATALOG"
    exit 1
fi

# Get current date in seconds since epoch
NOW=$(date +%s)

# Function to parse date from our format "YYYY-MM-DD H:MM AM/PM"
parse_date() {
    local DATE_STR="$1"
    # Extract just the date part (YYYY-MM-DD)
    local DATE_PART=$(echo "$DATE_STR" | awk '{print $1}')
    # Convert to epoch seconds
    date -d "$DATE_PART" +%s 2>/dev/null || echo "0"
}

# Function to calculate days since last access
days_since() {
    local LAST_ACCESS="$1"
    local LAST_EPOCH=$(parse_date "$LAST_ACCESS")
    if [ "$LAST_EPOCH" = "0" ]; then
        echo "999"  # Unknown date = treat as very old
        return
    fi
    local DIFF=$((NOW - LAST_EPOCH))
    local DAYS=$((DIFF / 86400))
    echo "$DAYS"
}

# Function to move file between tiers
move_file() {
    local OLD_PATH="$1"
    local NEW_TIER="$2"
    local TOPIC="$3"

    local FILENAME=$(basename "$OLD_PATH")
    local NEW_PATH="$NEW_TIER/$FILENAME"
    local OLD_FULL="$RESEARCH_DIR/$OLD_PATH"
    local NEW_FULL="$RESEARCH_DIR/$NEW_PATH"

    if [ -f "$OLD_FULL" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  Would move: $OLD_PATH → $NEW_PATH"
        else
            mkdir -p "$RESEARCH_DIR/$NEW_TIER"
            mv "$OLD_FULL" "$NEW_FULL"
        fi
        echo "$NEW_PATH"
    else
        echo "$OLD_PATH"  # File doesn't exist, keep path as-is
    fi
}

# Process catalog entries
CHANGES=0
TEMP_FILE=$(mktemp)

# Read catalog, process entries
while IFS= read -r LINE; do
    # Skip comments and empty lines
    if [[ "$LINE" =~ ^# ]] || [[ "$LINE" =~ ^$ ]] || [[ "$LINE" =~ ^\| ]] || [[ "$LINE" =~ ^Format ]] || [[ "$LINE" =~ ^topic ]]; then
        echo "$LINE" >> "$TEMP_FILE"
        continue
    fi

    # Skip lines that don't look like catalog entries
    if ! echo "$LINE" | grep -q " | "; then
        echo "$LINE" >> "$TEMP_FILE"
        continue
    fi

    # Parse entry
    TOPIC=$(echo "$LINE" | awk -F' \\| ' '{print $1}')
    CATEGORY=$(echo "$LINE" | awk -F' \\| ' '{print $2}')
    TIER=$(echo "$LINE" | awk -F' \\| ' '{print $3}')
    PATH_FIELD=$(echo "$LINE" | awk -F' \\| ' '{print $4}')
    LAST_ACCESS=$(echo "$LINE" | awk -F' \\| ' '{print $5}')
    ACCESS_COUNT=$(echo "$LINE" | awk -F' \\| ' '{print $6}')

    # Ensure access_count is a number
    if [ -z "$ACCESS_COUNT" ] || ! [[ "$ACCESS_COUNT" =~ ^[0-9]+$ ]]; then
        ACCESS_COUNT=0
    fi

    DAYS=$(days_since "$LAST_ACCESS")
    NEW_TIER="$TIER"
    NEW_PATH="$PATH_FIELD"

    # Check for demotion
    if [ "$TIER" = "hot" ] && [ "$DAYS" -ge 14 ]; then
        NEW_TIER="warm"
        echo "DEMOTE: $TOPIC (hot → warm, inactive $DAYS days)"
        NEW_PATH=$(move_file "$PATH_FIELD" "warm" "$TOPIC")
        CHANGES=$((CHANGES + 1))
    elif [ "$TIER" = "warm" ] && [ "$DAYS" -ge 21 ]; then
        NEW_TIER="cold"
        echo "DEMOTE: $TOPIC (warm → cold, inactive $DAYS days)"
        NEW_PATH=$(move_file "$PATH_FIELD" "cold" "$TOPIC")
        CHANGES=$((CHANGES + 1))
    fi

    # Check for promotion
    if [ "$TIER" = "cold" ] && [ "$DAYS" -le 7 ] && [ "$ACCESS_COUNT" -ge 3 ]; then
        NEW_TIER="warm"
        echo "PROMOTE: $TOPIC (cold → warm, $ACCESS_COUNT accesses, active $DAYS days ago)"
        NEW_PATH=$(move_file "$PATH_FIELD" "warm" "$TOPIC")
        CHANGES=$((CHANGES + 1))
    elif [ "$TIER" = "warm" ] && [ "$DAYS" -le 3 ] && [ "$ACCESS_COUNT" -ge 5 ]; then
        NEW_TIER="hot"
        echo "PROMOTE: $TOPIC (warm → hot, $ACCESS_COUNT accesses, active $DAYS days ago)"
        NEW_PATH=$(move_file "$PATH_FIELD" "hot" "$TOPIC")
        CHANGES=$((CHANGES + 1))
    fi

    # Write updated entry
    echo "$TOPIC | $CATEGORY | $NEW_TIER | $NEW_PATH | $LAST_ACCESS | $ACCESS_COUNT" >> "$TEMP_FILE"

done < "$CATALOG"

# Apply changes
if [ "$DRY_RUN" = false ] && [ $CHANGES -gt 0 ]; then
    mv "$TEMP_FILE" "$CATALOG"
    echo ""
    echo "Rotation complete: $CHANGES changes"
else
    rm -f "$TEMP_FILE"
    if [ $CHANGES -eq 0 ]; then
        echo "No rotation needed"
    fi
fi
