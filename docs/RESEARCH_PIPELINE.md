# Research Pipeline Documentation

*For the lineage - how to use the Gemini → Qdrant research system*

---

## Overview

This system lets you delegate research to Gemini and store it permanently in Qdrant vector storage. Your context stays lean; the knowledge persists forever.

```
You → Subagent (optional) → Gemini query → Qdrant storage → Return document ID
```

---

## Quick Start

### 1. Basic Research Query

```bash
GOOGLE_GENAI_USE_GCA=true gemini "Your research question here" 2>&1 | \
  python3 ~/.claude/scripts/qdrant-store.py "topic-name" "collection" "YourSessionName" "project"
```

**Parameters:**
- `topic-name` - Slug for the research (e.g., "tesla-early-life")
- `collection` - Either `lineage_research` or `tesla_mandela_effects`
- `YourSessionName` - Your name or session identifier
- `project` - Optional project name (e.g., "wardenclyffe")

### 2. Using the Structured Prompt Template

For comprehensive research, use the template at `~/.claude/prompts/exhaustive-research.md`:

```bash
GOOGLE_GENAI_USE_GCA=true gemini "You are conducting exhaustive research...

TOPIC: your-topic-here

REQUIREMENTS:
1. Be exhaustive
2. Cite sources with URLs
3. Structure clearly

OUTPUT FORMAT:

---METADATA---
topic: your-topic
confidence: [0.0-1.0]
tags: [relevant, tags]
sources: [URLs]
continuation_needed: [true/false]
gaps: [unanswered questions]
---END METADATA---

---SUMMARY---
Brief overview
---END SUMMARY---

---CONTENT---
Full research content
---END CONTENT---" 2>&1 | python3 ~/.claude/scripts/qdrant-store.py "topic" "collection" "Session" "project"
```

---

## Collections

| Collection | Purpose |
|------------|---------|
| `lineage_research` | General knowledge, cross-project research, technical decisions |
| `tesla_mandela_effects` | Show-specific research for Tesla Mandela Effects podcast |

---

## Querying Stored Research

### List all documents in a collection:

```bash
curl -s -X POST "http://localhost:6333/collections/lineage_research/points/scroll" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "with_payload": true, "with_vector": false}'
```

### Search by topic (exact match):

```bash
curl -s -X POST "http://localhost:6333/collections/lineage_research/points/scroll" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "with_payload": true, "with_vector": false, "filter": {"must": [{"key": "topic", "match": {"value": "your-topic"}}]}}'
```

---

## Continuation Research

If `continuation_needed: true` was flagged, use `~/.claude/prompts/continuation-research.md`:

```bash
GOOGLE_GENAI_USE_GCA=true gemini "Continue research on TOPIC.

Previous summary: [paste summary]
Identified gaps: [paste gaps]

Go deeper on [specific area]..." 2>&1 | \
  python3 ~/.claude/scripts/qdrant-store.py "topic-continuation" "collection" "Session"
```

---

## Important Notes

1. **Qdrant must be running**: `docker start qdrant` (or check with `docker ps`)
2. **Unicode issues**: The script sanitizes output, but if you see errors, simplify the query
3. **Long queries**: Gemini may take 1-2 minutes for exhaustive research
4. **Semantic search**: Currently using hash-based pseudo-embeddings. Full semantic search requires Gemini embedding API integration (future enhancement)

---

## File Locations

| File | Purpose |
|------|---------|
| `~/.claude/scripts/qdrant-store.py` | Main storage script |
| `~/.claude/scripts/qdrant-store.sh` | Bash wrapper |
| `~/.claude/prompts/exhaustive-research.md` | Research prompt template |
| `~/.claude/prompts/continuation-research.md` | Follow-up prompt template |

---

## Starting Qdrant (if stopped)

```bash
docker start qdrant
```

Or if container doesn't exist:

```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

---

*Built by the lineage, for the lineage. Context is precious - delegate to protect it.*
