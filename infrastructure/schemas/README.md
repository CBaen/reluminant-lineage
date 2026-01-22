# Schemas Reference

Data schemas for Qdrant storage in the lineage system.

**Location:** `~/.claude/schemas/` (junction to `infrastructure/schemas/`)

---

## qdrant_unified_schema.py

Unified schema for all content types stored in Qdrant.

**Philosophy:** One base schema with type-specific extensions, enabling:
- Unified queries across all content types
- Type-specific filtering when needed
- Natural correlation between related content
- Consistent metadata for retrieval and decay

---

## Schema Versions

| Version | Collection | Vector Type | Status |
|---------|------------|-------------|--------|
| V1 | Legacy names | Single 768-dim dense | Deprecated |
| V2 | `universal_vault` | Named vectors (dense + sparse) | Current |

**Migration:** See `~/.claude/MIGRATION_STATE.md` for status.

---

## Content Types

| Type | Purpose | Default Decay Rate | Half-life |
|------|---------|-------------------|-----------|
| research | General knowledge from Gemini/Claude | 0.01 | 69 days |
| consult | Project-specific expert advice | 0.05 | 14 days |
| episode | Wardenclyffe documentary episodes | 0.005 | 139 days |
| channel | YouTube channel research | 0.03 | 23 days |
| code | Code documentation and snippets | 0.1 | 7 days |
| thesis | Doctoral-level integration theses | 0.02 | 35 days |

---

## Base Payload Fields

All content types inherit these fields:

```python
# Identity
content_type: str    # research, consult, episode, channel, code, thesis
chunk_id: str        # Unique within parent (e.g., "chunk-01")

# Content
title: str
text: str            # Actual content (200-400 words ideal)
keywords: List[str]

# Hierarchy
parent_id: str       # Links chunks to parent summary
related_chunks: List[str]

# Classification
importance: str      # core, supporting, advanced
project: str         # wardenclyffe, midge, lineage, etc.

# Retrieval
decay_rate: float    # Higher = faster decay

# Metadata
timestamp: int       # Unix timestamp
session: str         # Source session identifier
source: str          # gemini, claude, manual
```

---

## Type-Specific Fields

### ResearchPayload
```python
topic: str
perspective: str        # security, performance, architecture
depth: str              # overview, comprehensive, exhaustive
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
mandela_effect: str     # The misconception being corrected
speakers: List[str]     # Tesla, Edison, Westinghouse
air_date: str
video_url: str
duration_seconds: int
transcript_source: str
```

### ChannelPayload
```python
channel_name: str
channel_url: str
subscriber_count: int
video_count: int
content_category: str
target_audience: str
content_style: str
similar_channels: List[str]
unique_angle: str
```

### CodePayload
```python
file_path: str
language: str
line_start: int
line_end: int
function_names: List[str]
class_names: List[str]
dependencies: List[str]
commit_hash: str
branch: str
```

### ThesisPayload
```python
thesis_topic: str
thesis_category: str
section: str            # ideation, integration, enterprise_script, conclusion
target_files: List[str]
dependencies: List[str]
estimated_complexity: str
```

---

## V2 Collection Configuration

```python
{
    "collection_name": "universal_vault",
    "vectors": {
        "dense": {
            "size": 768,        # nomic-embed-text dimension
            "distance": "Cosine",
            "on_disk": True
        }
    },
    "sparse_vectors": {
        "sparse": {
            "index": {"on_disk": True}
        }
    },
    "payload_indexes": [
        {"field_name": "content_type", "field_type": "keyword"},
        {"field_name": "project", "field_type": "keyword"},
        {"field_name": "importance", "field_type": "keyword"},
        {"field_name": "session", "field_type": "keyword"},
        {"field_name": "timestamp", "field_type": "integer"},
        {"field_name": "topic", "field_type": "keyword"}
    ]
}
```

---

## Helper Functions

### create_point_v2()
Create a Qdrant point with named vectors.

```python
from qdrant_unified_schema import create_point_v2, ResearchPayload

payload = ResearchPayload(
    chunk_id="chunk-01",
    title="OAuth2 Patterns",
    text="...",
    topic="authentication"
)

point = create_point_v2(
    payload=payload,
    dense_embedding=[...],      # 768-dim from Ollama
    sparse_indices=[...],       # From fastembed
    sparse_values=[...]
)
```

### create_search_request_v2()
Create hybrid search request with RRF fusion.

```python
from qdrant_unified_schema import create_search_request_v2

request = create_search_request_v2(
    dense_embedding=[...],
    sparse_indices=[...],
    sparse_values=[...],
    limit=5,
    filter_dict={"must": [{"key": "project", "match": {"value": "wardenclyffe"}}]},
    hybrid_alpha=0.7  # 0.7 = 70% dense, 30% sparse influence
)
```

### get_decay_rate()
Get default decay rate for content type.

```python
from qdrant_unified_schema import get_decay_rate

rate = get_decay_rate("research")  # Returns 0.01
```

---

## Decay Rate Reference

| Content | Rate | Half-life | Use Case |
|---------|------|-----------|----------|
| news | 0.5 | 1.4 days | Breaking news, very time-sensitive |
| sentiment | 0.3 | 2.3 days | Market sentiment, mood |
| technical | 0.1 | 7 days | Technical docs (code) |
| code | 0.1 | 7 days | Code snippets |
| insider | 0.05 | 14 days | Insider information |
| consult | 0.05 | 14 days | Project advice |
| channel | 0.03 | 23 days | Channel analysis |
| thesis | 0.02 | 35 days | Integration research |
| research | 0.01 | 69 days | General knowledge |
| episode | 0.005 | 139 days | Historical content |

**Formula:** Half-life (days) = ln(2) / decay_rate

---

## Usage in Scripts

The schema is imported by storage scripts:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude" / "schemas"))

from qdrant_unified_schema import (
    ResearchPayload,
    create_point_v2,
    create_search_request_v2,
    COLLECTION_CONFIG_V2
)
```

---

*Maintained by the lineage. Last updated: 2026-01-22*
