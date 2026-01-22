# catalog-search.sh

Search catalog by tag/category/keyword.

## What It Does

Searches the research catalog with various filters to find relevant research files.

## Usage

```bash
# By tag
catalog-search.sh --tag "caching"

# By category
catalog-search.sh --category "gemini"

# By tier
catalog-search.sh --tier "hot"

# By keyword in content
catalog-search.sh --keyword "react"

# List all
catalog-search.sh --all
```

## Options

| Option | Description |
|--------|-------------|
| `--tag` | Filter by tag in frontmatter |
| `--category` | Filter by category |
| `--tier` | Filter by storage tier (hot/warm/cold) |
| `--keyword` | Search content for keyword |
| `--all` | List all entries |

## Output

List of matching file paths, one per line.

## Dependencies

- Bash shell
- grep (for keyword search)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
