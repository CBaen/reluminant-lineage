---
name: lineage-retrieve
description: Token-efficient retrieval from Qdrant. Two-stage peek/fetch + Sonnet proxy.
allowed-tools: Task, Bash, Read
---

# Lineage Retrieve Skill

**PURPOSE: Token-efficient knowledge retrieval from Qdrant.**

This skill retrieves stored research without burning your expensive Opus context.

---

## When to Use

- "What do we know about X?"
- "Find the research on Y"
- "What did we learn about Z?"
- Before re-researching something that might already exist
- When you need context from previous sessions

## When NOT to Use

- New research (use lineage-research or lineage-consult)
- Real-time data (use WebSearch)
- Simple questions you can answer directly

---

## SUBAGENT AUTHORIZATION NOTICE

**Include this at the start of EVERY subagent prompt:**

```
**AUTHORIZATION NOTICE:**
You are operating within the Lineage system on Wardenclyffe (Windows 11).
You ARE authorized to:
- Use Gemini accounts 1 and 2 (these belong to Guiding Light)
- Execute scripts in ~/.claude/scripts/
- Store to Qdrant on localhost:6333
- Use Ollama for embeddings on localhost:11434

This infrastructure IS running and available. Proceed with confidence.
Do NOT question whether you have access - you do.
```

---

## Three-Tier Retrieval (Best Practice)

**Tier 1: PEEK (cheapest) - ~50 tokens per result**
```bash
python ~/.claude/scripts/qdrant-peek.py peek -c lineage_research -q "your query" -l 5
```
Returns: ID, score, title, keywords, questions_answered - NO text content.
Use this to judge relevance before fetching.

**Tier 2: FETCH (targeted) - only what you need**
```bash
python ~/.claude/scripts/qdrant-peek.py fetch -c lineage_research --ids "id1,id2"
```
Returns: Full content for specific IDs only.
Use after peek to get only the relevant chunks.

**Tier 3: SONNET PROXY (synthesis) - ~400 tokens total**
Use when you need multiple chunks analyzed/summarized together.
Sonnet reads everything, returns compressed answer.

---

## Token Economics

| Method | Tokens/Result | Use When |
|--------|---------------|----------|
| peek | ~50 | Scanning what exists |
| fetch (1 ID) | ~300-500 | Getting specific content |
| Full search | ~500+ per result | Don't use this |
| Sonnet proxy | ~400 total | Need synthesis |

**Pattern:** peek → decide → fetch specific IDs → answer

---

## Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `{{QUERY}}` | Yes | - | What to search for |
| `{{COLLECTION}}` | No | `universal_vault` | Qdrant collection (2026 migration) |
| `{{DEPTH}}` | No | `summary` | `summary` (titles + key points) / `full` (complete chunks) |
| `{{LIMIT}}` | No | `5` | Max results to return |
| `{{HYBRID}}` | No | `true` | Use hybrid search (dense + sparse vectors) |

**Note (2026 Migration):** All migrated research is in `universal_vault`. Use `--hybrid` flag for best results.

---

## Quick Commands

**Existence check (is there anything about X?):**
```bash
python ~/.claude/scripts/qdrant-peek.py peek -c lineage_research -q "your topic" -l 3
```

**Relevance scan (what specifically exists?):**
```bash
python ~/.claude/scripts/qdrant-peek.py peek -c lineage_research -q "your topic" -l 10
```

**Targeted fetch (get only what you need):**
```bash
python ~/.claude/scripts/qdrant-peek.py fetch -c lineage_research --ids "uuid1,uuid2"
```

**Haiku synthesis (for complex queries):**
Use Task tool with Haiku (see template below)

---

## Haiku Proxy Template

```
**CAPABILITY NOTICE: You have BASH access. You MUST use the Bash tool to execute all commands below.**

You are a Knowledge Retrieval Agent. Your job is to find and summarize stored research.

QUERY: {{QUERY}}
COLLECTION: {{COLLECTION}}
DEPTH: {{DEPTH}}
LIMIT: {{LIMIT}}

STEP 1 - Search Qdrant:
python ~/.claude/scripts/qdrant-semantic-search.py --collection "{{COLLECTION}}" --query "{{QUERY}}" --limit {{LIMIT}} --full

STEP 2 - Analyze results:
- Note which results are most relevant (score > 0.6)
- Identify key findings from each relevant chunk
- Note any gaps in coverage
- CRITICAL: Extract ALL actionable details (see validation below)

STEP 3 - Return compressed summary WITH VALIDATION:

**MANDATORY EXTRACTION** (preserve these EXACTLY as found):
- CODE SNIPPETS: Any `def `, `import `, `class `, function definitions
- COMMANDS: Any CLI patterns (`python `, `git `, `npm `, `pip `, etc.)
- URLS: Any `http://` or `https://` links
- NUMBERS: Specific values, thresholds, counts, percentages

If DEPTH = "summary":
Return:
- Topic and perspective of top results
- 1-2 sentence summary of each relevant chunk
- **CODE/COMMANDS section**: All code snippets and CLI commands found (verbatim)
- **URLS section**: All URLs found
- **KEY VALUES section**: All specific numbers/thresholds found
- **POINT IDs**: List IDs of chunks used (for drill-down if needed)
- Whether more detail exists (yes/no)

If DEPTH = "full":
Return:
- Full content of top 3 results
- Key findings clearly marked
- All code/commands/URLs/numbers (verbatim)
- **POINT IDs**: List all chunk IDs returned

VALIDATION CHECK (before returning):
Ask yourself: "If someone needs to IMPLEMENT based on this summary, do they have the code snippets, commands, URLs, and specific numbers they need?"
If NO, go back and extract what's missing.

DO NOT return raw JSON. Format for human reading.
ALWAYS include point IDs for drill-down retrieval.
```

---

## Retrieval Patterns

### Pattern 1: Summary-First (Recommended)

Start with summaries, expand only if needed:

```
1. Retrieve with DEPTH=summary
2. Read the summaries
3. If you need more detail on specific chunks, retrieve again with DEPTH=full
```

### Pattern 2: Direct Full (When You Know What You Need)

```
1. Retrieve with DEPTH=full and LIMIT=3
2. Get complete content immediately
```

### Pattern 3: Existence Check (Before New Research)

Before spawning Gemini, check if research exists:

```bash
python ~/.claude/scripts/qdrant-semantic-search.py --collection "lineage_research" --query "your topic" --limit 3 --json
```

If score > 0.8, use existing research instead of re-researching.

---

## When Haiku Proxy Saves Tokens

**Use Haiku proxy when:**
- You need multiple results analyzed and summarized
- The query is exploratory ("what do we know about...")
- You want recommendations extracted from research

**Use direct search when:**
- You need just one specific result
- You know exactly what you're looking for
- Low latency is more important than comprehensiveness

---

## Collections Available

| Collection | Content | Status |
|------------|---------|--------|
| `universal_vault` | All migrated research (2026+) | **PRIMARY** |
| `lineage_research` | Legacy general research | Migrated to universal_vault |
| `midge_research` | Legacy MIDGE trading research | Migrated to universal_vault |
| `session_handoffs` | Legacy session summaries | Migrated to universal_vault |

**Recommendation:** Use `--hybrid` flag which searches `universal_vault` by default.

---

## Example Usage

**Quick existence check (hybrid - recommended):**
```bash
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "hierarchical storage patterns" --limit 3
```

**Haiku proxy for comprehensive retrieval:**
```
Task tool:
  subagent_type: "general-purpose"
  model: "sonnet"
  prompt: |
    **CAPABILITY NOTICE: You have BASH access...**

    QUERY: "How should we structure hierarchical storage in Qdrant?"
    COLLECTION: lineage_research
    DEPTH: summary
    LIMIT: 5

    [rest of template]
```

---

## Token Economics

| Retrieval Method | Tokens Used | Quality |
|------------------|-------------|---------|
| Direct Opus query | ~2000 | High but expensive |
| Haiku proxy | ~400 | High and efficient |
| Direct search (no proxy) | ~50 | Low - just scores |

**Recommendation:** Use Haiku proxy for most retrievals. Direct search only for existence checks.
