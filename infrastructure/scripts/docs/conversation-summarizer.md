# conversation-summarizer.py

Generate summaries of conversations via Gemini.

## What It Does

Takes parsed and classified conversation data and generates concise summaries using Gemini, extracting key decisions, outcomes, and action items.

## Usage

```python
from conversation_summarizer import summarize_conversation

summary = summarize_conversation(messages, classifications, account=1)
```

## Output Structure

- Key decisions made
- Problems solved
- Files modified
- Action items
- Topics discussed

## Dependencies

- `google-generativeai`
- Gemini API credentials

## Changelog

- 2026-01-20: Initial creation (59ef471)
