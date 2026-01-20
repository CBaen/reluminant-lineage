# Lineage Workflow Reference

Detailed reference for the lineage workflow. The main skill file has the essentials - this document has advanced patterns and templates.

---

## Gemini Prompt Templates

### Maximizing Output

```
You are [EXPERT PERSONA].

I need comprehensive research on: [TOPIC]

Questions:
1. [Specific question]
2. [Specific question]

Structure with:
- Executive summary (2-3 sentences)
- Detailed findings for each question
- Code examples where applicable
- Edge cases and exceptions
- Key takeaways

Be exhaustive. This will be stored for future reference.
```

### Magic Phrases That Increase Output

| Phrase | Effect |
|--------|--------|
| "Be exhaustive" | Triggers comprehensive coverage |
| "Think step-by-step" | Activates chain-of-thought |
| "Stored for future reference" | Signals importance |
| "Cover edge cases" | Expands scope |
| "Do not stop early" | Prevents truncation |

### What Makes Gemini Stop Early (Avoid)

- Vague questions ("Tell me about X")
- No structure or format
- No persona assignment
- Asking for specific word counts

---

## Account Rotation Details

### Rate Limits

Per account:
- 60 requests/minute
- 1,000 requests/day

Two accounts = double capacity.

### Scripts

```bash
# Single query with specific account
~/.claude/scripts/gemini-account.sh 1 "query"
~/.claude/scripts/gemini-account.sh 2 "query"

# Parallel with rotation (odd=1, even=2)
~/.claude/scripts/gemini-parallel-rotate.sh "Q1" "Q2" "Q3"
```

### If Rate Limited

```bash
# If Account 1 rate-limits, use Account 2
# Both rate-limited? Wait 30 seconds, retry
```

### Credential Locations

```
~/.gemini/
├── oauth_creds.json           # Active credentials
├── google_accounts.json       # Active account info
├── oauth_creds_account1.json  # Account 1 backup
├── oauth_creds_account2.json  # Account 2 backup
```

---

## Qdrant Storage Details

### Collection

- Name: `lineage_research`
- Embeddings: Ollama nomic-embed-text (768 dimensions)
- Distance: Cosine

### What Gets Stored

```json
{
  "topic": "topic-name",
  "category": "gemini|documentation|decisions|explorations",
  "tags": ["tag1", "tag2"],
  "summary": "Brief for quick retrieval",
  "content": "Full detailed content",
  "session_name": "WhoStoredThis",
  "created_at": "2026-01-14T...",
  "embedding_source": "ollama",
  "confidence": 0.85
}
```

### Querying

```bash
# Hybrid search (recommended - searches universal_vault)
python ~/.claude/scripts/qdrant-semantic-search.py \
  --hybrid \
  --query "your question" \
  --limit 5

# Peek (token-efficient - titles only)
python ~/.claude/scripts/qdrant-peek.py peek \
  -c universal_vault \
  -q "your topic" -l 5

# Fetch specific IDs
python ~/.claude/scripts/qdrant-peek.py fetch \
  -c universal_vault \
  --ids "id1,id2"
```

---

## Flat File Storage

### Structure

```
~/.claude/research/
├── CATALOG.md      # Master index
├── hot/            # Frequently accessed
├── warm/           # Occasionally accessed
└── cold/           # Rarely accessed (preserved)
```

### Tier Rotation

Files move based on access, not time:
- Hot → Warm: No access 14+ days
- Warm → Cold: No access 21+ days
- Cold → Warm: Recent access + 3+ total accesses
- Warm → Hot: Very recent + 5+ total accesses

**Files are never deleted. Cold is the floor, not oblivion.**

### Living Topic Files

Same topic = same file. New research appends (newest at top):

```markdown
# Topic Name

## 2026-01-14 | Session: CurrentInstance
Latest findings...

---

## 2026-01-13 | Session: PreviousInstance
Earlier research...
```

---

## Parallel Subagent Pattern

For multiple independent research questions, spawn multiple Haiku subagents in ONE message:

```
[Message with multiple Task tool calls]

Task 1: Research authentication patterns
Task 2: Research database indexing
Task 3: Research caching strategies
```

Each runs in parallel. Each returns only paths. Maximum efficiency.

---

## Token Economics

| Pattern | Cost |
|---------|------|
| Direct Gemini in your context | ~3000+ tokens |
| Haiku summarizes for you | ~250 tokens |
| **Haiku orchestrates, returns path** | **~15 tokens** |

The path-only return pattern is 200x more efficient than direct calls.

---

## Troubleshooting

### Semantic Search Returns Empty

Check if points have `embedding_source: "ollama"`. Old points may have hash embeddings.

To re-embed: Delete and re-store with current pipeline.

### Gemini Times Out

- Simplify the question
- Use smaller scope
- Check account rotation (both may be rate-limited)

### Research Not Found But Exists

- Check spelling/normalization of topic
- Try semantic search instead of exact topic match
- Check both Qdrant and flat files (they're independent)
