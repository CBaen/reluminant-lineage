---
topic: "context-optimization"
category: "gemini"
tier: "hot"
tags:
  - "context"
  - "tokens"
  - "optimization"
  - "lazy-loading"
  - "pointers"
  - "rag"
  - "compression"
  - "budgeting"
  - "orchestrator"
created: "2026-01-11 02:08 PM"
last_accessed: "2026-01-14 06:05 AM"
access_count: 5
consolidated: "2026-01-11 04:00 PM"
---

# Context Window Optimization - Complete Guide

*Consolidated from basic and advanced research. Source: Gemini AI.*

---

## Part 1: Core Strategies

### 1.1 Summarization vs. Full Content

**Use Full Content when:**
- Code modification (exact syntax required)
- Error analysis (stack traces need full text)
- Legal/contractual analysis (nuance matters)

**Use Summarization for:**
- Initial triage (understand before diving deep)
- Conversation history (rolling summaries)
- Large documents (hierarchical chunk → summarize → summary-of-summaries)

**Hybrid Pattern (Best Practice):**
1. Generate high-level summary first
2. Use summary to identify relevant chunks
3. Load FULL content of relevant chunks only

### 1.2 Pointer/Reference Pattern

Instead of content in context, use **references**:
- File paths → agent reads when needed
- Database IDs → agent queries when needed
- URLs → agent fetches when needed

**Benefits:**
- Massive token savings
- Always fresh data
- Focused attention

### 1.3 Lazy Loading

"Just-in-time" information retrieval:
1. Plan the task
2. Find file path (pointer)
3. Read ONLY that file
4. Determine next file needed
5. Read ONLY that file

Never pre-load "everything you might need."

### 1.4 Metadata vs. Content Ratio

| Phase | Metadata | Content |
|-------|----------|---------|
| Planning | 80% | 20% |
| Code Writing | 20% | 80% |

Prioritize high-signal metadata (paths, signatures, objectives) over bulk content.

---

## Part 2: Advanced Compression Techniques

### 2.1 Beyond Simple Truncation

| Technique | Description | Token Savings |
|-----------|-------------|---------------|
| **Rolling Summaries** | Keep first + recent raw, compress middle | 60-70% |
| **Semantic Compression** | Embed → cluster → keep centroids | 50-70% |
| **Structured Extraction** | Convert prose to JSON | 60-80% |
| **Entity Extraction** | Keep only names, dates, facts | 70-90% |

**Key Insight:** Rolling summaries are the gold standard for conversations.

### 2.2 Production Overflow Handling

| Strategy | When to Use |
|----------|-------------|
| **Hybrid Raw + Summary** | Default for conversations |
| **Relevance-Scored Eviction** | When FIFO loses important context |
| **Async Summarization** | High-throughput systems |

**Relevance Scoring Formula:**
- Recency (newer = higher)
- Query similarity (embedding match)
- Explicit mentions (referenced = higher)

---

## Part 3: Cache vs. Fresh Retrieval (RAG)

### Decision Matrix

| Query Type | Use Cache | Use RAG |
|------------|-----------|---------|
| Conversational follow-up | ✅ | ❌ |
| Factual question | ❌ | ✅ |
| New unrelated task | Summarize old | Fresh context |

### The Orchestrator Pattern

A lightweight router classifies intent BEFORE main LLM processes:

```
User Query → [Orchestrator] → Intent Classification
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
 Follow-up   Factual    New Task
    ↓           ↓           ↓
 Use cache   Use RAG   Flush old
```

**Application to Lineage:** Router decides if cached research (Archive) suffices or subagent needed.

---

## Part 4: Context Budgeting

### Static Allocation (Recommended Start)

| Category | Budget | Purpose |
|----------|--------|---------|
| System Instructions | 10% | CLAUDE.md, identity |
| Project State | 15% | HANDOFF.md, blockers |
| Memory | 15% | MEMORY.md, patterns |
| Active Work | 40% | Current task, code |
| Subagent Results | 10% | Research summaries |
| Buffer | 10% | Flexibility |

### Dynamic Allocation

Reallocate unused budgets:
- No retrieved docs? → More for recent messages
- Heavy code task? → Shrink memory, expand active work

### Framework Support

- **LangChain**: `ConversationSummaryBufferMemory`
- **LlamaIndex**: `NodeParser` + `Retriever` with token limits

---

## Part 5: Lineage Implementation Recommendations

### Immediate Actions

1. **Use pointer pattern** for all research results (paths, not content)
2. **Delegate research** to subagents (their context, not main)
3. **Return minimal tokens** from subagents (~10 tokens max)

### Short-Term

4. **Implement rolling summaries** in HANDOFF.md (recent raw + compressed history)
5. **Add relevance scoring** to research archive (access_count + recency)
6. **Create orchestrator logic** for subagent routing

### Long-Term

7. **Build context manager** to enforce budget allocations
8. **Implement async summarization** for long sessions
9. **Add semantic search** to research archive

---

## Quick Reference: Token-Saving Patterns

```
❌ "Here's what I found: [500 tokens of explanation]..."
✅ "Stored: hot/topic.md" (5 tokens)

❌ Read all 6 research files at session start (6000 tokens)
✅ Grep for keywords, read only relevant sections (200 tokens)

❌ Return full Gemini response to main instance (2000 tokens)
✅ Store in archive, return path only (8 tokens)
```

---

*Consolidated 2026-01-11 from context-optimization + advanced-context-optimization*
