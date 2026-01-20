# Continuation Research Prompt Template

Use when previous research flagged `continuation_needed: true` or when deeper exploration is needed.

## Variables
- `{{TOPIC}}` - The original research topic
- `{{PREVIOUS_SUMMARY}}` - Summary from previous research
- `{{GAPS}}` - Gaps identified in previous research
- `{{FOCUS}}` - Specific area to go deeper on (optional)
- `{{COLLECTION}}` - Target collection
- `{{SESSION}}` - Session name

---

## Prompt

```
You are continuing research on a topic. Previous research was stored but flagged as incomplete.

TOPIC: {{TOPIC}}

PREVIOUS SUMMARY:
{{PREVIOUS_SUMMARY}}

IDENTIFIED GAPS:
{{GAPS}}

FOCUS AREA (if specified): {{FOCUS}}

YOUR TASK:
1. Address the gaps identified above
2. Go deeper on areas that were only surface-level
3. Find information that was previously unavailable
4. If a focus area is specified, prioritize that

REQUIREMENTS:
- Same standards as initial research (exhaustive, sourced, structured)
- Reference the previous research where relevant
- Don't repeat what's already known - ADD to it
- Flag any NEW gaps discovered

OUTPUT FORMAT (same as initial research):

---METADATA---
topic: {{TOPIC}}-continuation
confidence: [0.0-1.0]
tags: [include "continuation" tag]
sources: [new sources only]
continuation_needed: [true/false - is MORE still needed?]
gaps: [any remaining gaps]
---END METADATA---

---SUMMARY---
[What this continuation adds to previous knowledge]
---END SUMMARY---

---CONTENT---
[New findings that extend the previous research]

## Gaps Addressed
[Which gaps from previous research are now filled]

## New Discoveries
[Information not covered before]

## Remaining Unknowns
[What still couldn't be found]
---END CONTENT---
```

---

## When to Use

1. Previous research set `continuation_needed: true`
2. User asks "go deeper on X"
3. Gaps in previous research need filling
4. New context makes old research incomplete
