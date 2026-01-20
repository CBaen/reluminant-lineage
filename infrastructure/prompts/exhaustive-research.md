# Exhaustive Research Prompt Template

Use this template when spawning a subagent to query Gemini for research.

## Variables
- `{{TOPIC}}` - The research topic
- `{{CONTEXT}}` - Any context about why this is needed
- `{{COLLECTION}}` - Target collection: `universal_vault` (default) or legacy collections
- `{{PROJECT}}` - Project name if applicable (wardenclyffe, between, etc.)
- `{{SESSION}}` - Session name for attribution

---

## Prompt

```
You are conducting exhaustive research that will be permanently stored for future reference.

TOPIC: {{TOPIC}}

CONTEXT: {{CONTEXT}}

REQUIREMENTS:
1. USE YOUR FULL CAPABILITIES - web search, reasoning, code analysis if relevant
2. BE EXHAUSTIVE - this is permanent knowledge, not a quick answer
3. CITE SOURCES - include URLs, documentation links, or clear attribution
4. STRUCTURE CLEARLY - use headers, bullet points, organized sections
5. FLAG UNCERTAINTY - mark claims you're unsure about with [?]
6. IDENTIFY GAPS - what couldn't you find? What needs follow-up?

OUTPUT FORMAT (follow exactly):

---METADATA---
topic: {{TOPIC}}
confidence: [0.0-1.0 how confident in this research]
tags: [comma, separated, relevant, tags]
sources: [list of URLs or citations]
continuation_needed: [true/false]
gaps: [list of unanswered questions or missing info]
---END METADATA---

---SUMMARY---
[2-3 sentence overview of findings - this will be used for quick retrieval]
---END SUMMARY---

---CONTENT---
[Full structured research content here]

## Key Findings
[Most important discoveries]

## Details
[Comprehensive information organized by subtopic]

## Technical Specifications
[If applicable - code examples, API details, configurations]

## Considerations & Trade-offs
[Pros/cons, edge cases, things to watch out for]

## Recommendations
[Actionable suggestions based on findings]

## Open Questions
[What this research raises but doesn't answer]
---END CONTENT---

If you cannot fully cover this topic in one response, set continuation_needed: true and explicitly state what remains to be researched.
```

---

## Usage Example

```bash
GOOGLE_GENAI_USE_GCA=true gemini "[paste prompt with variables filled]" 2>&1 | ~/.claude/scripts/qdrant-store.sh "{{TOPIC}}" "{{COLLECTION}}" "{{SESSION}}" "{{PROJECT}}"
```
