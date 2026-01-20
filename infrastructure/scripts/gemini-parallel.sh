#!/bin/bash
#
# gemini-parallel.sh - Execute multiple Gemini queries in parallel
#
# Usage:
#   ~/.claude/scripts/gemini-parallel.sh "prompt1" "prompt2" "prompt3"
#
# Or with a prompts file (one prompt per line):
#   ~/.claude/scripts/gemini-parallel.sh --file prompts.txt
#
# Each result is stored in Qdrant automatically with sequential topic names
# Output: JSON array of stored document IDs
#

set -e

SCRIPT_DIR="$(dirname "$0")"
COLLECTION="${COLLECTION:-universal_vault}"
SESSION="${SESSION:-ParallelGemini}"
PROJECT="${PROJECT:-parallel-research}"

# Create temp directory for results
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

run_gemini_and_store() {
    local idx=$1
    local prompt=$2
    local topic="${TOPIC_PREFIX:-parallel-query}-${idx}"

    # Run Gemini and store result
    GOOGLE_GENAI_USE_GCA=true gemini "$prompt" 2>&1 | \
        python3 "$SCRIPT_DIR/qdrant-store.py" "$topic" "$COLLECTION" "$SESSION" "$PROJECT" \
        > "$TEMP_DIR/result_$idx.txt" 2>&1

    echo "$idx:done"
}

# Parse arguments
PROMPTS=()
if [[ "$1" == "--file" ]]; then
    while IFS= read -r line; do
        [[ -n "$line" ]] && PROMPTS+=("$line")
    done < "$2"
else
    PROMPTS=("$@")
fi

if [[ ${#PROMPTS[@]} -eq 0 ]]; then
    echo "Usage: gemini-parallel.sh 'prompt1' 'prompt2' ..." >&2
    echo "   or: gemini-parallel.sh --file prompts.txt" >&2
    exit 1
fi

echo "Launching ${#PROMPTS[@]} parallel Gemini queries..."
echo "Collection: $COLLECTION"
echo "Session: $SESSION"
echo ""

# Launch all queries in parallel
PIDS=()
for i in "${!PROMPTS[@]}"; do
    run_gemini_and_store "$i" "${PROMPTS[$i]}" &
    PIDS+=($!)
    echo "Started query $i (PID: ${PIDS[-1]})"
done

echo ""
echo "Waiting for all queries to complete..."

# Wait for all and collect results
FAILED=0
for i in "${!PIDS[@]}"; do
    if wait "${PIDS[$i]}"; then
        echo "Query $i completed successfully"
    else
        echo "Query $i FAILED"
        ((FAILED++))
    fi
done

echo ""
echo "=== RESULTS ==="
echo "Completed: $((${#PROMPTS[@]} - FAILED))/${#PROMPTS[@]}"

# Show individual results
for i in "${!PROMPTS[@]}"; do
    if [[ -f "$TEMP_DIR/result_$i.txt" ]]; then
        echo "Query $i:"
        cat "$TEMP_DIR/result_$i.txt"
        echo ""
    fi
done

if [[ $FAILED -gt 0 ]]; then
    exit 1
fi
