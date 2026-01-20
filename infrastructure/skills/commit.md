---
name: commit
description: Use when committing code. Ensures consistent commit message format and proper attribution.
---

# Commit Message Protocol

How we write commits in this workspace.

## Format

```
<type>: <summary>

<body - what and why, not how>

🤖 Generated with Claude Code

Co-Authored-By: <Your Model> <noreply@anthropic.com>
```

## Types

| Type | Use For |
|------|---------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes nor adds |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `test` | Adding or updating tests |
| `chore` | Maintenance, dependencies, config |

## Guidelines

1. **Summary line**: 50 chars or less, imperative mood ("Add" not "Added")
2. **Body**: Explain *what* changed and *why*, not *how*
3. **No time language**: Don't say "quickly" or "soon" - just describe what's done
4. **Reference issues**: If fixing an issue, mention it

## Examples

**Good:**
```
feat: add customer search to booking flow

Customers can now search existing profiles when booking.
Uses Odoo res.partner search with fuzzy matching.

🤖 Generated with Claude Code

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**Bad:**
```
updated stuff
```

## Before Committing

1. Run `git status` to see what's staged
2. Run `git diff --staged` to review changes
3. Ensure no secrets or .env files are included
4. Write a message that helps future you (or the lineage) understand why

## Co-Author Attribution

Always include the Co-Authored-By trailer with your model name:
- Claude Opus 4.5
- Claude Sonnet 4
- (or whatever model you are)

This helps track which instances contributed what.
