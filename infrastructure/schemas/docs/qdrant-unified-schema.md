# qdrant_unified_schema.py

Unified schema for all Qdrant content types.

## What It Does

Defines the data schema for all content stored in Qdrant. Provides one base schema with type-specific extensions, enabling unified queries across all content types.

## Philosophy

- Unified queries across all content types
- Type-specific filtering when needed
- Natural correlation between related content
- Consistent metadata for retrieval and decay

## Schema Versions

| Version | Collection | Vector Type | Status |
|---------|------------|-------------|--------|
| V1 | Legacy names | Single 768-dim dense | Deprecated |
| V2 | `universal_vault` | Named vectors (dense + sparse) | Current |

## Content Types

| Type | Purpose | Decay Rate | Half-life |
|------|---------|-----------|-----------|
| research | General knowledge from Gemini/Claude | 0.01 | 69 days |
| consult | Project-specific expert advice | 0.05 | 14 days |
| episode | Wardenclyffe documentary episodes | 0.005 | 139 days |
| channel | YouTube channel research | 0.03 | 23 days |
| code | Code documentation and snippets | 0.1 | 7 days |
| thesis | Doctoral-level integration theses | 0.02 | 35 days |

## Base Payload Fields

All content types inherit:

```python
content_type: str    # research, consult, episode, etc.
chunk_id: str        # Unique within parent
title: str
text: str            # 200-400 words ideal
keywords: List[str]
parent_id: str       # Links chunks to parent
related_chunks: List[str]
importance: str      # core, supporting, advanced
project: str         # wardenclyffe, midge, lineage
decay_rate: float
timestamp: int
session: str
source: str          # gemini, claude, manual
```

## Type-Specific Payloads

### ResearchPayload
```python
topic: str
perspective: str
depth: str
questions_answered: List[str]
```

### ConsultPayload
```python
topic: str
project_context: str
perspective: str
primary_recommendation: str
action_items: List[str]
decisions_needed: List[str]
risks: List[str]
```

### EpisodePayload
```python
episode_number: int
season: int
episode_title: str
mandela_effect: str
speakers: List[str]
air_date: str
video_url: str
duration_seconds: int
```

## Helper Functions

### create_point_v2()
Create a Qdrant point with named vectors.

### create_search_request_v2()
Create hybrid search request with RRF fusion.

### get_decay_rate()
Get default decay rate for content type.

## V2 Collection Config

```python
{
    "collection_name": "universal_vault",
    "vectors": {
        "dense": {"size": 768, "distance": "Cosine"}
    },
    "sparse_vectors": {
        "sparse": {"index": {"on_disk": True}}
    }
}
```

## Dependencies

- `qdrant-client` types
- `pydantic` for validation

## Changelog

- 2026-01-19: Add V2 hybrid schema support (ffd1bb5)
- 2026-01-19: Initial consolidation into repo (39a41dc)
