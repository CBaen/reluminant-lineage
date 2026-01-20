---
name: lineage-conversations
description: Search indexed conversation history. Find past decisions, file changes, errors, and discussions.
allowed-tools: Bash, Read, Task
---

# Lineage Conversations Skill

**PURPOSE: Search past Claude Code conversations for decisions, file changes, errors, and discussions.**

This skill provides searchable access to your conversation history. Ask questions like:
- "What changes did we make to auth.py?"
- "Why did we choose PostgreSQL?"
- "What errors happened during the Qdrant migration?"

---

## When to Use

- Finding past decisions and their reasoning
- Remembering what files were changed and why
- Looking up how an error was fixed
- Finding discussions about a specific topic
- Understanding why something was implemented a certain way

## When NOT to Use

- General knowledge research (use lineage-research)
- Real-time data (use WebSearch)
- Project-specific guidance (use lineage-consult)

---

## Quick Search Commands

**Search conversation history:**
```bash
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "your question" --limit 5
```

The results will include conversation exchanges tagged with `research_type: conversation_index`.

**Filter specifically for conversation history:**
```bash
# Search with filter (more precise)
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "auth.py changes" --filter '{"must":[{"key":"research_type","match":{"value":"conversation_index"}}]}' --limit 5
```

---

## Example Queries

| You Want To Find | Search Query |
|------------------|--------------|
| Changes to a file | "changes to auth.py" or "modified auth.py" |
| Why something was done | "why did we use PostgreSQL" or "reasoning for choosing X" |
| How an error was fixed | "error with database connection" or "fixed the migration issue" |
| A specific decision | "decided to use Redux" or "architecture decision for state" |
| Implementation details | "implemented the user authentication" |

---

## Indexing Status

**Check what's been indexed:**
```bash
python ~/.claude/scripts/conversation-indexer.py --status
```

**Index new conversations:**
```bash
python ~/.claude/scripts/conversation-indexer.py
```

**Re-index everything:**
```bash
python ~/.claude/scripts/conversation-indexer.py --reindex
```

**Index a specific session:**
```bash
python ~/.claude/scripts/conversation-indexer.py --session-id <session-uuid>
```

---

## Understanding Results

Indexed conversations are categorized into:

| Category | What It Means |
|----------|---------------|
| `decision` | Architecture, design, or approach decisions |
| `file_change` | Code modifications, edits, file creation |
| `error_fix` | Bug fixes, error resolution |
| `discussion` | Technical discussions |
| `implementation` | Feature building |
| `research` | Investigation and exploration |

Results include:
- **title**: Brief description of the exchange
- **content**: Summary of what happened and why
- **keywords**: Searchable terms
- **questions_answered**: What questions this exchange answers
- **importance**: high/medium/low

---

## Integration with Other Skills

**Pattern: Check conversations before researching**

Before spawning new research, check if you already discussed it:
```bash
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "your topic" --limit 3
```

If you find relevant conversation history, use that context instead of re-researching.

---

## Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `{{QUERY}}` | Yes | - | What to search for |
| `{{LIMIT}}` | No | `5` | Max results to return |

---

## Subagent Template (For Comprehensive Search)

```
**CAPABILITY NOTICE: You have BASH access. You MUST use the Bash tool.**

You are searching conversation history for: {{QUERY}}

STEP 1 - Search conversation index:
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "{{QUERY}}" --limit {{LIMIT}}

STEP 2 - Analyze results:
- Identify which results are most relevant (score > 0.6)
- Extract key decisions, file changes, or error fixes
- Note file paths mentioned
- Capture reasoning and context

STEP 3 - Return summary:
Format:
- **Found X relevant exchanges**
- For each relevant result:
  - What happened
  - Why (if known)
  - Files involved
  - Outcome
- **Key takeaways**: What should the main instance know

DO NOT return raw JSON. Format for human reading.
```

---

## Maintenance

**Nightly auto-indexing (optional):**
Can be configured via Windows Task Scheduler to run:
```bash
python ~/.claude/scripts/conversation-indexer.py --account 1
```

**Manual maintenance:**
```bash
# See what would be indexed
python ~/.claude/scripts/conversation-indexer.py --dry-run

# Index without Gemini (faster, lower quality summaries)
python ~/.claude/scripts/conversation-indexer.py --no-gemini
```

---

## How It Works

1. **Parser** reads raw conversation JSONL files
2. **Classifier** identifies important exchanges (decisions, file changes, errors)
3. **Summarizer** uses Gemini to create searchable descriptions
4. **Qdrant** stores with hybrid vectors for semantic + keyword search

The system automatically tracks what's been indexed, so running it again only processes new/changed conversations.

---

## Troubleshooting

**No results found:**
- Check if conversations have been indexed: `python ~/.claude/scripts/conversation-indexer.py --status`
- Try broader search terms
- Check Qdrant is running: `curl http://localhost:6333/collections`

**Outdated results:**
- Re-run indexer: `python ~/.claude/scripts/conversation-indexer.py`
- Force re-index specific session: `python ~/.claude/scripts/conversation-indexer.py --session-id <id> --reindex`

**Slow indexing:**
- Use `--no-gemini` for faster (but lower quality) indexing
- Reduce batch size: `--batch-size 5`
