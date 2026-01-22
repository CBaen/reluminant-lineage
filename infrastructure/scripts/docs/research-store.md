# research-store.sh

Store research with YAML frontmatter.

## What It Does

Stores research content to the flat-file catalog with proper YAML frontmatter for metadata. Handles consolidation by appending to existing files.

## Usage

```bash
echo "content" | research-store.sh "topic" "category" "session" ["tags"] ["project-path"]
```

## Arguments

| Position | Description | Required |
|----------|-------------|----------|
| 1 | Topic name | Yes |
| 2 | Category | Yes |
| 3 | Session identifier | Yes |
| 4 | Comma-separated tags | No |
| 5 | Project path override | No |

## YAML Frontmatter

```yaml
---
topic: "topic-name"
category: "category"
session: "session-id"
tags: [tag1, tag2]
created: "2026-01-22"
updated: "2026-01-22"
---
```

## Consolidation

If file for topic exists, content is appended with separator. Updated timestamp is refreshed.

## Dependencies

- Bash shell
- Catalog directory structure

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
