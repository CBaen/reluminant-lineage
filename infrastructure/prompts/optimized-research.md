# Optimized Research Prompt Template v2

Based on meta-research findings from the system analyzing itself.

## Key Optimizations Applied
- Persona adoption (expert role)
- Explicit structured template with numbered sections
- Chain-of-thought instruction
- Specific artifacts requested
- "Exhaustive" combined with concrete structure

---

## Variables
- `{{TOPIC}}` - The research topic
- `{{CONTEXT}}` - Why this research matters
- `{{COLLECTION}}` - Target collection
- `{{SESSION}}` - Session name for attribution

---

## Prompt

```
You are a domain expert and senior researcher. Your task is to produce an EXHAUSTIVE research document.

TOPIC: {{TOPIC}}

CONTEXT: {{CONTEXT}}

INSTRUCTIONS:
1. Think step-by-step through everything relevant to this topic
2. Do not stop until you have covered every major aspect
3. Use web search to find current, authoritative sources
4. Cite all sources with URLs

REQUIRED OUTPUT STRUCTURE (fill in ALL sections completely):

---METADATA---
topic: {{TOPIC}}
confidence: [0.0-1.0]
tags: [at least 5 relevant tags]
sources: [all URLs used]
entities: [key people, organizations, technologies mentioned]
continuation_needed: [true/false]
gaps: [specific unanswered questions]
---END METADATA---

---SUMMARY---
[3-5 sentences capturing the essential findings. This will be indexed for quick retrieval.]
---END SUMMARY---

---CONTENT---

# 1. Overview
[Comprehensive introduction to the topic - at least 3 paragraphs]

# 2. Key Concepts
[Define and explain 5-10 core concepts, each with a full paragraph]

# 3. Historical Context
[How did we get here? Timeline and evolution]

# 4. Current State
[What is the situation today? Major players, approaches, trends]

# 5. Technical Details
[Deep dive into specifics - code, configurations, architectures, or processes]

# 6. Case Studies / Examples
[3-5 real-world examples with specific details]

# 7. Common Pitfalls & Best Practices
[What to avoid, what works]

# 8. Future Directions
[Where is this heading? Emerging trends]

# 9. Action Items
[Specific, actionable recommendations]

# 10. Open Questions
[What remains unknown or contested?]

---END CONTENT---

IMPORTANT: Complete ALL 10 sections thoroughly. Each section should be substantive (multiple paragraphs). Do not summarize or truncate. This is permanent research that will be stored forever.
```

---

## Usage

```bash
GOOGLE_GENAI_USE_GCA=true gemini "[paste optimized prompt with variables filled]" 2>&1 | \
  python3 ~/.claude/scripts/qdrant-store.py "{{TOPIC}}" "{{COLLECTION}}" "{{SESSION}}" "project"
```

---

## Why This Works (from meta-research)

1. **"Domain expert and senior researcher"** - Persona triggers expert-mode verbosity
2. **"Think step-by-step"** - Chain-of-thought externalizes reasoning
3. **"Do not stop until..."** - Explicit instruction against early termination
4. **10 numbered sections** - Template structure is the strongest "unlock"
5. **"Complete ALL sections thoroughly"** - Redundant reinforcement
6. **"Each section should be substantive"** - Explicit length expectation
7. **"permanent research stored forever"** - Stakes increase perceived importance
