#!/bin/bash
# gemini-parallel-rotate.sh - Run multiple Gemini queries rotating between accounts
#
# Usage:
#   gemini-parallel-rotate.sh "query1" "query2" "query3" "query4"
#
# Odd queries use Account 1, even queries use Account 2
# Results are stored to Qdrant via research-pipeline.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEMINI_DIR="$HOME/.gemini"

if [[ $# -lt 1 ]]; then
    echo "Usage: gemini-parallel-rotate.sh \"query1\" \"query2\" ..." >&2
    exit 1
fi

# Function to swap account
swap_account() {
    local acct="$1"
    if [[ "$acct" == "1" ]]; then
        cp "$GEMINI_DIR/oauth_creds_account1.json" "$GEMINI_DIR/oauth_creds.json"
        cp "$GEMINI_DIR/google_accounts_account1.json" "$GEMINI_DIR/google_accounts.json"
    else
        cp "$GEMINI_DIR/oauth_creds_account2.json" "$GEMINI_DIR/oauth_creds.json"
        cp "$GEMINI_DIR/google_accounts_account2.json" "$GEMINI_DIR/google_accounts.json"
    fi
}

# Process queries - alternate between accounts
count=1
for query in "$@"; do
    # Determine account (odd=1, even=2)
    if (( count % 2 == 1 )); then
        account=1
    else
        account=2
    fi

    echo "Query $count (Account $account): ${query:0:50}..." >&2

    # Swap to account and run query
    swap_account "$account"

    # Generate topic from query (first 3 words, normalized)
    topic=$(echo "$query" | awk '{print $1"-"$2"-"$3}' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')

    # Run through research pipeline (handles storage to both Qdrant and flat files)
    "$SCRIPT_DIR/research-pipeline.sh" "$topic-$count" "$query" "ParallelResearch" "parallel,batch" &

    count=$((count + 1))
done

# Wait for all background jobs
echo "Waiting for all queries to complete..." >&2
wait

echo "All $# queries completed"
