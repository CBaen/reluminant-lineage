# external_bridge.py

Unified external knowledge access.

## What It Does

Provides a unified interface for accessing external knowledge sources: local LLM (Oracle), web search, Wikipedia, and the knowledge store.

## Usage

```python
from external_bridge import ExternalBridge

bridge = ExternalBridge()

# Query Oracle (local LLM)
result = bridge.ask_oracle("question")

# Web search
results = bridge.web_search("query")

# Wikipedia
article = bridge.wikipedia("topic")

# Knowledge store
knowledge = bridge.knowledge_store("topic")
```

## Capabilities

| Method | Source | Use Case |
|--------|--------|----------|
| `ask_oracle()` | Local LLM | Quick factual queries |
| `web_search()` | Web | Current information |
| `wikipedia()` | Wikipedia | Background knowledge |
| `knowledge_store()` | Qdrant | Previously researched |

## Dependencies

- Ollama (for Oracle)
- Web search API
- `wikipedia` package
- `qdrant-client`

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
