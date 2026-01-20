#!/bin/bash
# =============================================================================
# gemini-swarm-worker.sh - Swarm worker with account locking
# =============================================================================
#
# Acquires a Gemini account lock, runs research, stores to Qdrant, releases lock.
# Used by swarm supervisors for parallel research without account conflicts.
#
# Usage:
#   gemini-swarm-worker.sh "topic" "perspective" "collection" "session" "depth"
#
# Session naming convention: [project]-[model]-[YYYY-MM-DD]
# Examples:
#   gemini-swarm-worker.sh "topic" "general" "midge_research" "midge-gemini-2026-01-14"
#   gemini-swarm-worker.sh "topic" "general" "lineage_research" "lineage-gemini-2026-01-14"
#
# =============================================================================

set -e

LOCK_DIR="$HOME/.claude/locks"
GEMINI_DIR="$HOME/.gemini"
SCRIPTS_DIR="$HOME/.claude/scripts"

# Generate default session name: [collection prefix]-gemini-[date]
DEFAULT_SESSION="research-gemini-$(date +%Y-%m-%d)"

TOPIC="${1:-}"
PERSPECTIVE="${2:-general}"
COLLECTION="${3:-universal_vault}"
SESSION="${4:-$DEFAULT_SESSION}"
DEPTH="${5:-comprehensive}"

if [[ -z "$TOPIC" ]]; then
    echo "Usage: gemini-swarm-worker.sh <topic> [perspective] [collection] [session] [depth]" >&2
    exit 1
fi

# Ensure lock directory exists
mkdir -p "$LOCK_DIR"

# Try to acquire an account lock
acquire_account() {
    for account in 1 2; do
        lockfile="$LOCK_DIR/gemini_account_${account}.lock"

        # Try to create lock file atomically
        if (set -o noclobber; echo "$$" > "$lockfile") 2>/dev/null; then
            echo "$account"
            return 0
        fi

        # Check if lock is stale (older than 5 minutes)
        if [[ -f "$lockfile" ]]; then
            lock_age=$(($(date +%s) - $(stat -c %Y "$lockfile" 2>/dev/null || echo 0)))
            if [[ $lock_age -gt 300 ]]; then
                rm -f "$lockfile"
                if (set -o noclobber; echo "$$" > "$lockfile") 2>/dev/null; then
                    echo "$account"
                    return 0
                fi
            fi
        fi
    done

    # No account available - wait and retry
    sleep 5
    acquire_account
}

release_account() {
    local account="$1"
    rm -f "$LOCK_DIR/gemini_account_${account}.lock"
}

# Acquire account
ACCOUNT=$(acquire_account)
trap "release_account $ACCOUNT" EXIT

# Swap to acquired account
if [[ "$ACCOUNT" == "1" ]]; then
    cp "$GEMINI_DIR/oauth_creds_account1.json" "$GEMINI_DIR/oauth_creds.json"
    cp "$GEMINI_DIR/google_accounts_account1.json" "$GEMINI_DIR/google_accounts.json"
else
    cp "$GEMINI_DIR/oauth_creds_account2.json" "$GEMINI_DIR/oauth_creds.json"
    cp "$GEMINI_DIR/google_accounts_account2.json" "$GEMINI_DIR/google_accounts.json"
fi

# Build the prompt
PROMPT="You are a research expert AND semantic chunking specialist preparing data for Qdrant vector database.

TARGET SYSTEM: Qdrant with semantic search + metadata filtering.

RESEARCH TASK:
- Topic: $TOPIC
- Perspective: $PERSPECTIVE
- Context: general
- Depth: $DEPTH

OUTPUT: Return ONLY valid JSON (no markdown, no explanation):

{
  \"meta\": {
    \"topic\": \"$TOPIC\",
    \"perspective\": \"$PERSPECTIVE\",
    \"context\": \"general\",
    \"depth\": \"$DEPTH\",
    \"total_words\": 0,
    \"chunk_count\": 0
  },
  \"summary\": {
    \"text\": \"2-4 sentence executive summary\",
    \"keywords\": [\"keyword1\", \"keyword2\"]
  },
  \"chunks\": [
    {
      \"id\": \"chunk-01\",
      \"title\": \"Section Title\",
      \"content\": \"200-400 words of focused research content\",
      \"keywords\": [\"specific\", \"keywords\"],
      \"questions_answered\": [\"What question does this answer?\"],
      \"related_chunks\": [\"chunk-02\"],
      \"importance\": \"core\"
    }
  ]
}

CHUNKING RULES:
- Each chunk = ONE coherent concept (semantic, not word-count splits)
- 200-400 words per chunk (optimal for embedding)
- Depth determines chunk count: overview=4-6, comprehensive=8-12, exhaustive=15-25
- keywords = search terms to find this chunk
- questions_answered = queries this answers (critical for retrieval)
- importance: core (must-know), supporting (examples), advanced (edge cases)

Return ONLY JSON."

# Run Gemini and store results using temp files (Windows pipe buffering fix)
export GOOGLE_GENAI_USE_GCA=true
echo "[Worker $ACCOUNT] Researching: $TOPIC ($PERSPECTIVE)" >&2

# Use temp files to avoid Windows pipe buffering issues with large outputs
TEMP_RAW="/tmp/gemini_worker_${$}_raw.txt"
TEMP_JSON="/tmp/gemini_worker_${$}_extracted.json"

# Cleanup temp files on exit
cleanup_temps() {
    rm -f "$TEMP_RAW" "$TEMP_JSON"
}
trap "release_account $ACCOUNT; cleanup_temps" EXIT

# Run Gemini, output to file
gemini -m gemini-2.5-flash "$PROMPT" > "$TEMP_RAW" 2>&1
EXIT_CODE=$?

# Check for rate limiting errors
if grep -qi "quota\|rate.limit\|capacity\|exhausted\|429" "$TEMP_RAW"; then
    echo "[Worker $ACCOUNT] RATE LIMITED - cooling down 60s before release" >&2

    # Write cooldown timestamp to lock file
    echo "COOLDOWN:$(date +%s):$$" > "$LOCK_DIR/gemini_account_${ACCOUNT}.lock"

    sleep 60  # Hold lock during cooldown

    # Retry once after cooldown
    echo "[Worker $ACCOUNT] Retrying after cooldown..." >&2
    gemini -m gemini-2.5-flash "$PROMPT" > "$TEMP_RAW" 2>&1
    EXIT_CODE=$?

    if grep -qi "quota\|rate.limit\|capacity\|exhausted\|429" "$TEMP_RAW"; then
        echo "[Worker $ACCOUNT] Still rate limited after retry - failing" >&2
        cat "$TEMP_RAW" >&2
        exit 1
    fi
fi

# Process successful output: file -> extract -> file -> store
echo "[Worker $ACCOUNT] Extracting JSON from $(wc -c < "$TEMP_RAW") bytes..." >&2
python "$SCRIPTS_DIR/extract-json.py" < "$TEMP_RAW" > "$TEMP_JSON" 2>&1

if [[ ! -s "$TEMP_JSON" ]] || grep -q '"error"' "$TEMP_JSON" 2>/dev/null; then
    echo "[Worker $ACCOUNT] JSON extraction failed" >&2
    cat "$TEMP_JSON" >&2
    exit 1
fi

echo "[Worker $ACCOUNT] Storing to Qdrant..." >&2
python "$SCRIPTS_DIR/qdrant-store-gemini.py" --collection "$COLLECTION" --session "$SESSION" < "$TEMP_JSON"
