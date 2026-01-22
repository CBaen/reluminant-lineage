# qdrant-store.sh

**DEPRECATED** - Use `qdrant-chunked-store.py` instead.

## What It Does

Shell wrapper for the basic qdrant-store.py script. Superseded by the Python chunked storage script.

## Replacement

```bash
cat content.json | python qdrant-chunked-store.py --topic "topic"
```

## Changelog

- 2026-01-19: Deprecated - replaced by qdrant-chunked-store.py
- 2026-01-19: Initial consolidation into repo (39a41dc)
