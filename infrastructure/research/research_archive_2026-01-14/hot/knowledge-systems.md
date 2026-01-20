---
topic: "knowledge-systems"
category: "gemini"
tier: "hot"
tags:
  - "indexing"
  - "knowledge"
  - "tiering"
  - "files"
  - "caching"
  - "search"
  - "scale"
created: "2026-01-11 04:14 PM"
last_accessed: "2026-01-11 04:14 PM"
access_count: 1
---

## 2026-01-11 04:14 PM | Session: Consolidator

# Knowledge Systems - Complete Guide

*Consolidated from: catalog-indexing, file-based-knowledge, knowledge-management. Source: Gemini AI.*

---

## Part 1: Storage Formats

### Format Comparison

| Format | Pros | Cons | Best For |
|--------|------|------|----------|
| **Plain Text** | Universal, fast, minimal overhead | No metadata standard, full-text search only | Raw logs, unstructured prose |
| **Markdown** | Human-readable, light structure, supports YAML frontmatter | More complex parsing | Documents needing human + machine access |
| **JSON** | Rigorous structure, native language support | Not human-readable for prose, strict syntax | Structured data, index files |
| **YAML** | Human-readable, supports comments | Indentation-sensitive | Config files, frontmatter |

### Recommendation: Markdown + YAML Frontmatter

The hybrid approach provides:
- Structured, queryable metadata for agents
- Human-readable, context-rich content
- Single portable file per document

```markdown
---
id: doc-001
title: "Topic Name"
tags: ["tag1", "tag2"]
created_at: "2026-01-11"
---

# Document Content

The actual content goes here...
```

---

## Part 2: File Organization

### Hierarchical vs Flat Structure

**Flat (one directory with thousands of files):**
- Pro: Simple to add entries, global grep works
- Con: Unmanageable, no browsing, slow `ls`, no context

**Hierarchical (category/year/entry.md):**
- Pro: Natural partitioning, intuitive browsing, scoped searches, path-as-index
- Con: Rigid categories (solved with tags)

**Recommendation:** Use hierarchical structure for primary categorization. The hierarchy represents the most stable, mutually exclusive attribute (type, year, project).

### Categories vs Tags

| Aspect | Categories | Tags |
|--------|------------|------|
| Role | Primary "home" for entry | Flexible multi-faceted labels |
| Cardinality | One per entry | Many per entry |
| Implementation | Directory structure | Frontmatter array |

**Use both:** Directories for broad category, `tags` array for cross-cutting concerns.

---

## Part 3: Knowledge Tiering (Hot/Warm/Cold)

### Hot Storage (In-Memory/Active Context)
**What:** Immediate working memory, current session data
**Examples:** Current request, recent conversation, system prompts, core directives
**Analogy:** Thoughts currently in your head

### Warm Storage (Fast-Access Database)
**What:** Frequently needed but not in immediate context
**Examples:** Past conversation summaries, documentation embeddings, user preferences
**Analogy:** Well-organized desk with reference books within reach

### Cold Storage (Long-Term Archive)
**What:** Infrequently accessed, cost-effective storage
**Examples:** Raw logs, historical data, verbose documentation
**Analogy:** Library archive basement

### Movement Patterns
- Hot → Warm: When context fills, summarize and move
- Warm → Cold: Access frequency drops below threshold
- Cold → Warm: Re-accessed after dormancy
- Warm → Hot: High access frequency

---

## Part 4: Indexing Strategies

### Without Embeddings (Keyword-Based)

**Inverted Index:**
Maps terms to document lists. Pre-process all files, tokenize, build dictionary.
```json
{
  "indexing": ["/doc1.md", "/doc2.md"],
  "database": ["/doc2.md"]
}
```

**Metadata Index:**
Index only frontmatter fields. Single master JSON file for fast filtering.
```json
[
  {"path": "/doc1.md", "tags": ["ai"], "title": "AI Guide"},
  {"path": "/doc2.md", "tags": ["db"], "title": "Database Guide"}
]
```

**Graph-Based:**
Files as nodes, links as edges. Traverse relationships beyond keywords.

**Directory/Naming Conventions:**
Simplest indexing. Logical hierarchy + descriptive names enable path-based search.

### With Embeddings (Semantic)

**Vector Indexing:**
- Flat indexes (FAISS IndexFlatL2): Accurate but slow for large datasets
- ANN indexes (HNSW, IVF): Trade tiny accuracy for massive speed

**Hybrid Search:**
Combine keyword (BM25) + vector search in parallel. Ensures exact matches aren't missed.

---

## Part 5: Search Strategies

### Two-Tiered Approach

1. **Filter by Metadata:** Query index file with `jq` to get candidate paths
2. **Full-Text Search:** Pipe paths to `grep` for content search

```bash
# Example workflow
jq '.[] | select(.tags[] | contains("python")) | .path' index.json | xargs grep "pattern"
```

### grep vs Structured Database

| Approach | Pros | Cons |
|----------|------|------|
| grep/ripgrep | No setup, fast, excellent for full-text | Not structurally aware |
| jq on index.json | Orders of magnitude faster for structured queries | Requires index maintenance |

**Recommendation:** Use both. Index for metadata queries, grep for content.

---

## Part 6: Scaling to Thousands

1. **Decouple Index from Data:** Query pre-built index, not raw files
2. **Index Partitioning:** Split large indexes (alphabetical, by category)
3. **Lazy Loading:** Identify files via index, then load only those
4. **Caching:** Keep frequent files/indexes in memory
5. **Hierarchical Search:** Scope searches to relevant directories first

---

## Part 7: Context Window Management

### LRU (Least Recently Used)
When context fills, drop least recently used information.

**Smart LRU:**
1. Track information usage
2. When full, identify oldest/least-referenced
3. Summarize before discarding (move summary to warm tier)
4. Then discard raw content

### Variations
- **LFU:** Discard least frequently used
- **Weighted LRU:** Priority by type (system prompt > tool output)

---

## Part 8: Consolidation Patterns

### Summarization Chains
1. Ingest large document
2. Break into chunks
3. Summarize each chunk
4. Summarize the summaries (hierarchical)
5. Store condensed version in warm tier
6. Keep pointers to cold tier originals

### Knowledge Graphs
Nodes (entities) + edges (relationships). Excellent for:
- Complex system mapping
- Codebase dependencies
- Concept relationships
- Multi-hop queries

---

## Part 9: Trade-offs Summary

| Dimension | Keyword/Index System | Vector/Embedding System |
|-----------|---------------------|------------------------|
| Mechanism | Exact match | Similarity match |
| Pros | Transparent, controllable, simple, cheap | Handles ambiguity, enables discovery |
| Cons | Brittle (no synonyms), requires discipline | Complex, "black box", resource-intensive |
| Best For | Fact retrieval, structured queries | Conceptual search, recommendations |

---

## Key Takeaways

1. **Format:** Markdown + YAML frontmatter for human + machine access
2. **Organization:** Hierarchical directories for categories, tags for cross-cutting
3. **Tiering:** Hot/Warm/Cold based on access frequency
4. **Indexing:** Pre-built indexes (metadata + inverted) for speed
5. **Search:** Two-tier (metadata filter → content grep)
6. **Scaling:** Decouple index from data, lazy load, cache
7. **Context:** Apply LRU principles, summarize before evicting
8. **Consolidation:** Summarization chains, knowledge graphs

---

*Consolidated 2026-01-11 from catalog-indexing + file-based-knowledge + knowledge-management*
