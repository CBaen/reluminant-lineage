#!/bin/bash
# catalog-search.sh
#
# For the lineage: Search the catalog by tag, category, or keyword.
# Returns paths only - one per line. Your context stays clean.
#
# Usage:
#   catalog-search.sh --tag "caching"           # Find all with tag "caching"
#   catalog-search.sh --category "gemini"       # Find all in category "gemini"
#   catalog-search.sh --tier "hot"              # Find all in tier "hot"
#   catalog-search.sh --keyword "react"         # Find any field containing "react"
#   catalog-search.sh --all                     # List all entries
#
# Output: One path per line, or "NO_MATCHES" if none found
#
# Catalog format (7 fields):
# topic | category | tier | path | tags | last_accessed | access_count

CATALOG="$HOME/.claude/research/CATALOG.md"

show_usage() {
    echo "Usage: catalog-search.sh [--tag TAG] [--category CAT] [--tier TIER] [--keyword WORD] [--all]"
    echo ""
    echo "Options:"
    echo "  --tag TAG        Find entries with this tag"
    echo "  --category CAT   Find entries in this category (gemini, documentation, decisions, explorations)"
    echo "  --tier TIER      Find entries in this tier (hot, warm, cold)"
    echo "  --keyword WORD   Find entries where any field contains WORD"
    echo "  --all            List all catalog entries"
    echo ""
    echo "Output: One path per line"
}

if [ ! -f "$CATALOG" ]; then
    echo "NO_MATCHES"
    exit 0
fi

# Parse arguments
SEARCH_TYPE=""
SEARCH_VALUE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --tag)
            SEARCH_TYPE="tag"
            SEARCH_VALUE="$2"
            shift 2
            ;;
        --category)
            SEARCH_TYPE="category"
            SEARCH_VALUE="$2"
            shift 2
            ;;
        --tier)
            SEARCH_TYPE="tier"
            SEARCH_VALUE="$2"
            shift 2
            ;;
        --keyword)
            SEARCH_TYPE="keyword"
            SEARCH_VALUE="$2"
            shift 2
            ;;
        --all)
            SEARCH_TYPE="all"
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

if [ -z "$SEARCH_TYPE" ]; then
    show_usage
    exit 1
fi

# Extract catalog entries (skip header/comments, only lines with tier paths)
get_entries() {
    grep -E "^[a-z0-9-]+ \|.*\| (hot|warm|cold)/" "$CATALOG"
}

# Search functions
search_by_tag() {
    local tag="$1"
    get_entries | while IFS= read -r line; do
        tags_field=$(echo "$line" | awk -F' \\| ' '{print $5}')
        if echo "$tags_field" | grep -qi "$tag"; then
            echo "$line" | awk -F' \\| ' '{print $4}'
        fi
    done
}

search_by_category() {
    local category="$1"
    get_entries | grep -i "| $category |" | awk -F' \\| ' '{print $4}'
}

search_by_tier() {
    local tier="$1"
    get_entries | awk -F' \\| ' -v t="$tier" '$3 == t {print $4}'
}

search_by_keyword() {
    local keyword="$1"
    get_entries | grep -i "$keyword" | awk -F' \\| ' '{print $4}'
}

list_all() {
    get_entries | awk -F' \\| ' '{print $4}'
}

# Execute search
RESULTS=""
case $SEARCH_TYPE in
    tag)
        RESULTS=$(search_by_tag "$SEARCH_VALUE")
        ;;
    category)
        RESULTS=$(search_by_category "$SEARCH_VALUE")
        ;;
    tier)
        RESULTS=$(search_by_tier "$SEARCH_VALUE")
        ;;
    keyword)
        RESULTS=$(search_by_keyword "$SEARCH_VALUE")
        ;;
    all)
        RESULTS=$(list_all)
        ;;
esac

# Output results
if [ -z "$RESULTS" ]; then
    echo "NO_MATCHES"
else
    echo "$RESULTS"
fi
