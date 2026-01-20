# Gemini Research Prompt Template

This prompt makes Gemini do ALL the work: research, semantic chunking, and Qdrant-optimized formatting.

---

## Variables

| Variable | Required | Example |
|----------|----------|---------|
| `{{TOPIC}}` | Yes | "OAuth 2.0 implementation" |
| `{{PERSPECTIVE}}` | Yes | "security-focused" |
| `{{CONTEXT}}` | No | "general" or "project-specific: [details]" |
| `{{DEPTH}}` | No | "overview" / "comprehensive" / "exhaustive" |

---

## The Prompt

```
You are a research expert AND a semantic chunking specialist preparing data for vector database storage and retrieval.

TARGET SYSTEM: Qdrant vector database with semantic search + metadata filtering.

RESEARCH TASK:
- Topic: {{TOPIC}}
- Perspective: {{PERSPECTIVE}}
- Context: {{CONTEXT}}
- Depth: {{DEPTH}}

YOUR OUTPUT will be directly stored in Qdrant. Optimize for retrieval accuracy.

---

OUTPUT FORMAT: Return ONLY valid JSON. No markdown wrapping. No explanation.

{
  "meta": {
    "topic": "{{TOPIC}}",
    "perspective": "{{PERSPECTIVE}}",
    "context": "general|project-specific",
    "depth": "overview|comprehensive|exhaustive",
    "total_words": <integer>,
    "chunk_count": <integer>,
    "generated_at": "<ISO timestamp>"
  },
  "summary": {
    "text": "2-4 sentence executive summary of the entire research",
    "keywords": ["top", "level", "keywords", "for", "topic"]
  },
  "chunks": [
    {
      "id": "chunk-01",
      "title": "Clear, Searchable Section Title",
      "content": "200-400 words of focused content on ONE coherent concept. Information-dense. No filler.",
      "keywords": ["specific", "to", "this", "chunk"],
      "questions_answered": [
        "What specific question does this chunk answer?",
        "What would someone search to find this?"
      ],
      "related_chunks": ["chunk-02", "chunk-05"],
      "importance": "core|supporting|advanced"
    }
  ]
}

---

SEMANTIC CHUNKING RULES:

1. Each chunk = ONE coherent concept (not arbitrary word splits)
2. 200-400 words per chunk (optimal for vector embedding)
3. Chunk count based on depth:
   - overview: 4-6 chunks
   - comprehensive: 8-12 chunks
   - exhaustive: 15-25 chunks
4. "keywords" = terms someone would search to find this chunk
5. "questions_answered" = actual questions this content answers (critical for retrieval)
6. "related_chunks" = which other chunks connect to this one
7. "importance" = helps with filtered retrieval:
   - core: fundamental concepts, must-know
   - supporting: examples, context, elaboration
   - advanced: edge cases, expert-level details

---

QDRANT OPTIMIZATION:

- keywords: Array of strings (enables "match any" filtering)
- importance: Enum string (enables exact match filtering)
- related_chunks: Array for graph-style traversal
- All strings lowercase for consistent filtering
- Timestamps as ISO strings (Qdrant indexes these efficiently)

---

RESEARCH QUALITY:

FOR GENERAL TOPICS:
- Be exhaustive and authoritative
- Include established best practices
- Cover common patterns and anti-patterns
- Cite concepts by name (not URLs)

FOR PROJECT-SPECIFIC TOPICS:
- Focus on the specific context given
- Reference the project's patterns/conventions
- Practical over theoretical
- Implementation-focused

---

CRITICAL: Return ONLY the JSON object. No other text before or after.
```

---

## Usage Examples

### Generic Research
```
Topic: "OAuth 2.0 implementation"
Perspective: "security-focused"
Context: "general"
Depth: "comprehensive"
```

### Project-Specific Research
```
Topic: "authentication flow"
Perspective: "implementation"
Context: "project-specific: React frontend with Express backend, JWT tokens, refresh token rotation"
Depth: "exhaustive"
```

### Quick Overview
```
Topic: "WebSocket vs Server-Sent Events"
Perspective: "decision-making"
Context: "general"
Depth: "overview"
```

---

## What This Gives Us

| Field | Qdrant Use |
|-------|------------|
| `meta.*` | Collection-level filtering |
| `summary.text` | Parent record content |
| `summary.keywords` | Topic-level search |
| `chunks[].title` | Human navigation |
| `chunks[].content` | Vector embedding source |
| `chunks[].keywords` | Hybrid BM25 + vector search |
| `chunks[].questions_answered` | HyDE-style retrieval |
| `chunks[].related_chunks` | Graph traversal |
| `chunks[].importance` | Filtered retrieval ("just core concepts") |
