#!/bin/bash
# Changelog reminder hook for infrastructure changes
# Runs after Edit/Write in infrastructure/ to remind about changelog updates

# Get the file path from environment
FILE_PATH="$CLAUDE_TOOL_FILE_PATH"

# Skip if no file path
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Check if file is in infrastructure/ (but not a CHANGELOG.md itself)
if [[ "$FILE_PATH" == *"/infrastructure/"* ]] || [[ "$FILE_PATH" == *"\\infrastructure\\"* ]]; then
    # Skip if this IS a changelog file
    if [[ "$FILE_PATH" == *"CHANGELOG.md" ]]; then
        exit 0
    fi

    # Extract the folder name for the reminder
    # This works for paths like /infrastructure/scripts/foo.py -> scripts
    FOLDER=$(echo "$FILE_PATH" | sed -E 's|.*[/\\]infrastructure[/\\]([^/\\]+)[/\\].*|\1|')

    echo "CHANGELOG REMINDER: You modified infrastructure/$FOLDER/. Update infrastructure/$FOLDER/CHANGELOG.md with what changed."
fi

exit 0
