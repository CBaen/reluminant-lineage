#!/bin/bash
# =============================================================================
# gemini-account.sh - Multi-Account Gemini CLI Wrapper with AUTO-FALLBACK
# =============================================================================
#
# PURPOSE:
#   Run Gemini CLI queries with AUTOMATIC MODEL FALLBACK.
#   ALWAYS starts with highest quality models, falls back to lower quality.
#   Tries both accounts for each model before moving to next model.
#   NEVER gives up until ALL models on ALL accounts are exhausted.
#
# PHILOSOPHY:
#   Quality over speed. Always. Research is stored in Qdrant for fast retrieval.
#   Generating lower-quality research to save time defeats the purpose.
#
# FALLBACK CHAIN (Quality-First, Always):
#   1. gemini-2.5-pro (Account 1, then 2) - HIGHEST quality, 100/day each
#   2. gemini-3-pro-preview (Account 1, then 2) - Newest pro, 100/day each
#   3. gemini-3-flash-preview (Account 1, then 2) - Good quality, unlimited
#   4. gemini-2.5-flash (Account 1, then 2) - Good quality, unlimited
#   5. gemini-2.5-flash-lite (Account 1, then 2) - Fallback, 1,500/day each
#
# USAGE:
#   gemini-account.sh 1 "your query"              # Quality-first (always)
#   gemini-account.sh 1 "query" gemini-2.5-pro    # Start with specific model
#   gemini-account.sh 1 "query" --no-fallback     # Disable fallback
#
# ACCOUNTS:
#   1 = cameronbpaul@gmail.com
#   2 = cbaenp@protonmail.com
#
# MODEL QUOTAS (each is a SEPARATE pool):
#   gemini-2.5-pro            - 100/day per account (200 total) [HIGHEST QUALITY]
#   gemini-3-pro-preview      - 100/day per account (200 total) [NEWEST PRO]
#   gemini-3-flash-preview    - Unlimited (rate limited only)
#   gemini-2.5-flash          - Unlimited (rate limited only)
#   gemini-2.5-flash-lite     - 1,500/day per account (3,000 total)
#
# IMPORTANT: Each model has its OWN quota pool. 2.5-pro exhaustion does NOT
# affect 3-pro-preview quota. You should NEVER run out entirely - just rotate.
#
# CREATED: January 2026 by the Lineage
# UPDATED: January 2026 - Quality-first always, no speed mode
# =============================================================================

set +e

GEMINI_DIR="$HOME/.gemini"
FALLBACK_LOG="$GEMINI_DIR/fallback.log"

# Parse arguments
ACCOUNT="${1:-1}"
QUERY="${2:-}"
MODEL=""
NO_FALLBACK=false

# Check for flags in arguments 3 and 4
for arg in "$3" "$4"; do
    case "$arg" in
        --no-fallback)
            NO_FALLBACK=true
            ;;
        gemini-*)
            MODEL="$arg"
            ;;
    esac
done

# Retry configuration
MAX_RETRIES=2
BASE_DELAY=3  # 3 seconds per account minimum

# =============================================================================
# MODEL FALLBACK CHAIN - Quality First, Always
# Each model has its OWN quota pool. Rotate accounts before switching models.
# =============================================================================

# Quality-first chain - Pro models first, then Flash, then lite
# This is the ONLY chain. Quality over speed, always.
MODEL_CHAIN=(
    "gemini-2.5-pro"            # HIGHEST quality, 100/day per account
    "gemini-3-pro-preview"      # Newest pro, 100/day per account
    "gemini-3-flash-preview"    # Good quality, unlimited
    "gemini-2.5-flash"          # Good quality, unlimited
    "gemini-2.5-flash-lite"     # Fallback, 1,500/day per account
)

DEFAULT_MODEL="gemini-2.5-pro"

# Set default model if not specified
if [[ -z "$MODEL" ]]; then
    MODEL="$DEFAULT_MODEL"
fi

if [[ -z "$QUERY" ]]; then
    echo "Usage: gemini-account.sh <1|2> \"your query\" [options]" >&2
    echo "" >&2
    echo "Options:" >&2
    echo "  --no-fallback   Disable auto-fallback, fail on first quota error" >&2
    echo "  gemini-*        Start with specific model" >&2
    echo "" >&2
    echo "Accounts:" >&2
    echo "  1 = cameronbpaul@gmail.com" >&2
    echo "  2 = cbaenp@protonmail.com" >&2
    echo "" >&2
    echo "Models (each has SEPARATE quota pool):" >&2
    echo "  gemini-2.5-pro          - 100/day per account [HIGHEST QUALITY - DEFAULT]" >&2
    echo "  gemini-3-pro-preview    - 100/day per account [NEWEST PRO]" >&2
    echo "  gemini-3-flash-preview  - Unlimited (rate limited)" >&2
    echo "  gemini-2.5-flash        - Unlimited (rate limited)" >&2
    echo "  gemini-2.5-flash-lite   - 1,500/day per account" >&2
    echo "" >&2
    echo "Fallback Chain (Quality-First, Always):" >&2
    echo "  2.5-pro → 3-pro → 3-flash → 2.5-flash → lite" >&2
    echo "" >&2
    echo "Behavior:" >&2
    echo "  - ALWAYS starts with highest quality model (gemini-2.5-pro)" >&2
    echo "  - Each model is a SEPARATE quota pool (never truly exhausted)" >&2
    echo "  - Tries both accounts on each model before moving to next" >&2
    echo "  - Quality over speed. Always." >&2
    exit 1
fi

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Swap to requested account
swap_account() {
    local acct="$1"
    if [[ "$acct" == "1" ]]; then
        cp "$GEMINI_DIR/oauth_creds_account1.json" "$GEMINI_DIR/oauth_creds.json" 2>/dev/null
        cp "$GEMINI_DIR/google_accounts_account1.json" "$GEMINI_DIR/google_accounts.json" 2>/dev/null
    elif [[ "$acct" == "2" ]]; then
        cp "$GEMINI_DIR/oauth_creds_account2.json" "$GEMINI_DIR/oauth_creds.json" 2>/dev/null
        cp "$GEMINI_DIR/google_accounts_account2.json" "$GEMINI_DIR/google_accounts.json" 2>/dev/null
    else
        echo "Invalid account: $acct (use 1 or 2)" >&2
        return 1
    fi
}

# Log fallback events
log_fallback() {
    local msg="$1"
    local timestamp=$(/usr/bin/date '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "TIMESTAMP_ERROR")
    echo "[$timestamp] $msg" >> "$FALLBACK_LOG"
    echo "[FALLBACK] $msg" >&2
}

# Check if response indicates RATE LIMIT (temporary, can retry)
# NOTE: Check this FIRST - "exhausted your capacity" is rate limit, not quota
is_rate_limited() {
    local response="$1"

    # Rate limit patterns - these are TEMPORARY, retry after delay
    # "exhausted your capacity" = rate limit (per-minute), NOT daily quota
    if [[ "$response" == *"429"* ]] || \
       [[ "$response" == *"rate limit"* ]] || \
       [[ "$response" == *"rate_limit"* ]] || \
       [[ "$response" == *"too many requests"* ]] || \
       [[ "$response" == *"Too many requests"* ]] || \
       [[ "$response" == *"exhausted your capacity"* ]] || \
       [[ "$response" == *"capacity"* && "$response" != *"daily"* ]] || \
       [[ "$response" == *"RESOURCE_EXHAUSTED"* && "$response" != *"daily"* && "$response" != *"quota"* ]]; then
        return 0  # true - rate limited, can retry after delay
    fi
    return 1  # false
}

# Check if response indicates QUOTA EXHAUSTION (daily limit, need to switch models)
# NOTE: Only triggers for DAILY quota, not temporary rate limits
is_quota_exhausted() {
    local response="$1"

    # True quota exhaustion - these are DAILY limits, need to switch models/accounts
    # Must explicitly mention "daily", "quota exceeded", or "quota" with "limit"
    if [[ "$response" == *"daily"* && "$response" == *"limit"* ]] || \
       [[ "$response" == *"daily"* && "$response" == *"quota"* ]] || \
       [[ "$response" == *"quota"* && "$response" == *"exceeded"* ]] || \
       [[ "$response" == *"quota"* && "$response" == *"exhausted"* ]] || \
       [[ "$response" == *"RESOURCE_EXHAUSTED"* && "$response" == *"quota"* ]]; then
        return 0  # true - daily quota exhausted, need fallback
    fi
    return 1  # false
}

# Check if response indicates model not found
is_model_not_found() {
    local response="$1"

    if [[ "$response" == *"not found"* ]] || \
       [[ "$response" == *"NOT_FOUND"* ]] || \
       [[ "$response" == *"does not exist"* ]] || \
       [[ "$response" == *"invalid model"* ]]; then
        return 0  # true
    fi
    return 1  # false
}

# Get index of model in chain
get_model_index() {
    local model="$1"
    local i=0
    for m in "${MODEL_CHAIN[@]}"; do
        if [[ "$m" == "$model" ]]; then
            echo $i
            return
        fi
        ((i++))
    done
    echo -1  # Not found
}

# Try a single model+account combination
try_model() {
    local model="$1"
    local account="$2"
    local attempt=1
    local delay=$BASE_DELAY
    local output
    local exit_code

    swap_account "$account"

    while [[ $attempt -le $MAX_RETRIES ]]; do
        # Call via PowerShell on Windows for reliable execution
        # Escape query for PowerShell
        escaped_query=$(printf '%s' "$QUERY" | sed "s/'/\\'/g")
        # Use positional prompt with --output-format text for simple responses
        output=$(powershell.exe -NonInteractive -Command "gemini -m '$model' --output-format text '$escaped_query'" 2>&1)
        exit_code=$?

        # Success!
        if [[ $exit_code -eq 0 ]] && ! is_rate_limited "$output" && ! is_quota_exhausted "$output" && ! is_model_not_found "$output"; then
            echo "$output"
            return 0
        fi

        # Check RATE LIMIT FIRST - this is temporary, retry with backoff
        if is_rate_limited "$output"; then
            if [[ $attempt -lt $MAX_RETRIES ]]; then
                echo "[RATE_LIMIT] Attempt $attempt failed, waiting ${delay}s before retry..." >&2
                sleep $delay
                delay=$((delay * 2))
                ((attempt++))
                continue
            fi
            # Persistent rate limit after retries - switch account/model
            return 2
        fi

        # Quota exhausted (daily limit) - signal caller to try next model
        if is_quota_exhausted "$output"; then
            return 2  # Special code: quota exhausted
        fi

        # Model not found - signal caller to try next
        if is_model_not_found "$output"; then
            return 3  # Special code: model not available
        fi

        # Other error - return it
        echo "$output"
        return $exit_code
    done

    return 1
}

# =============================================================================
# MAIN FALLBACK LOGIC
# =============================================================================

execute_with_fallback() {
    local start_model="$MODEL"
    local start_account="$ACCOUNT"
    local output
    local result

    # Find starting position in model chain
    local start_idx=$(get_model_index "$start_model")
    if [[ $start_idx -eq -1 ]]; then
        start_idx=0  # Start from beginning if model not in chain
    fi

    # Try each model in the chain
    for ((i=start_idx; i<${#MODEL_CHAIN[@]}; i++)); do
        local current_model="${MODEL_CHAIN[$i]}"

        # Try account 1
        output=$(try_model "$current_model" "1")
        result=$?

        if [[ $result -eq 0 ]]; then
            # Success!
            if [[ "$current_model" != "$start_model" || "1" != "$start_account" ]]; then
                log_fallback "SUCCESS: $start_model/acct$start_account -> $current_model/acct1"
            fi
            echo "$output"
            return 0
        fi

        if [[ $result -eq 2 || $result -eq 3 ]]; then
            # Quota exhausted or model not found on account 1, try account 2
            output=$(try_model "$current_model" "2")
            result=$?

            if [[ $result -eq 0 ]]; then
                log_fallback "SUCCESS: $start_model/acct$start_account -> $current_model/acct2"
                echo "$output"
                return 0
            fi

            if [[ $result -eq 2 || $result -eq 3 ]]; then
                # Both accounts exhausted for this model, try next model
                log_fallback "SKIP: $current_model exhausted on both accounts"
                continue
            fi
        fi

        # Other error - return it
        echo "$output"
        return $result
    done

    # All models exhausted
    log_fallback "FAILED: All models exhausted on all accounts"
    echo "ERROR: All Gemini models exhausted on all accounts. Tried: ${MODEL_CHAIN[*]}" >&2
    return 1
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

# GCA = Google Cloud Authentication (uses Google Sign-In OAuth flow)
export GOOGLE_GENAI_USE_GCA=true

if [[ "$NO_FALLBACK" == "true" ]]; then
    # Old behavior - just try the one model
    swap_account "$ACCOUNT"
    gemini -m "$MODEL" "$QUERY"
else
    # New behavior - automatic fallback through all models
    execute_with_fallback
fi
