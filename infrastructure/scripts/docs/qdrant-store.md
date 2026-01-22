# qdrant-store.py

**DEPRECATED** - Use `qdrant-chunked-store.py` instead.

## What It Does

Basic Qdrant storage script. Superseded by the chunked storage script which handles proper chunking and parent-child relationships.

## Replacement

```bash
# Instead of qdrant-store.py, use:
cat content.json | python qdrant-chunked-store.py --topic "topic"
```

## Changelog

- 2026-01-19: Deprecated - replaced by qdrant-chunked-store.py
- 2026-01-19: Initial consolidation into repo (39a41dc)
