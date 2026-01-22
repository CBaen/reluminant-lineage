# conversation-classifier.py

Classify conversation content by type and topic.

## What It Does

Analyzes parsed conversation messages and classifies them by content type (code discussion, debugging, architecture, etc.) and topic areas.

## Usage

```python
from conversation_classifier import classify_conversation

classifications = classify_conversation(messages)
```

## Classification Categories

- Code Discussion
- Debugging
- Architecture
- Documentation
- Research
- Planning
- General

## Dependencies

- None (rule-based classification)

## Changelog

- 2026-01-20: Initial creation (59ef471)
