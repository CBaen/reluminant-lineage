# Wardenclyffe Qdrant Schema Design

**Source**: Research agent aea601b + Deep Gemini Research (2026-01-15)
**Status**: READY FOR IMPLEMENTATION

---

## Critical Findings from Deep Research

### Token-Efficient Fact Extraction (IMPORTANT)

| Approach | Token Cost (12K-word episode) | Accuracy | Verdict |
|----------|-------------------------------|----------|---------|
| **Full Episode to LLM** | ~19,100-20,200 tokens | HIGHEST | **RECOMMENDED** |
| Chunk-then-extract | ~23,100-25,200 tokens | Context loss risk | NOT recommended |
| Regex/NLP first | ~4,000 tokens | HIGH false-negative rate | NOT recommended |
| Two-pass | ~87,500 tokens | Balanced but expensive | NOT recommended |

**Why Full Episode Wins**: For episodes under 16,000 words, sending the entire transcript to Gemini is:
- Actually CHEAPER than chunking (no overlap overhead, no deduplication logic)
- MORE ACCURATE (LLM has full context for relationships, implied facts)
- SIMPLER (one API call, not 7-8 chunk calls)

### Version Control Strategy

**Use `status` field, not separate collections:**
- `active` - current version being used
- `superseded` - replaced by newer version
- `draft` - in progress, not approved
- `error` - version had issues, rolled back

**Rollback = status update** (not delete/recreate):
1. Set erroneous version to `status: "error"`
2. Set previous version to `status: "active"`
3. Full audit trail preserved

### Parent-Child Relationships

**Qdrant has NO native parent-child support.** Model explicitly:
- Store parent IDs in child payloads (`series_id`, `episode_id`, `scene_id`)
- Query children: filter by `parent_id` match
- Cascade delete: Application logic (query children → delete children → delete parent)

**Denormalization is CORRECT for Qdrant** - include parent IDs in all children for fast queries.

---

## Collections Overview

| Collection | Purpose |
|------------|---------|
| `episodes` | Episode drafts with segment-level versioning |
| `canon_facts` | Extracted facts that constrain future episodes |
| `episode_outputs` | CAPTION, TTS_VERSION, CAPTION_KEY files |

---

## 1. Episodes Collection

**Purpose**: Store episode drafts with granular editing and version control.

### Schema

```json
{
  "episode_id": "003",
  "segment_id": "scene-05",
  "version": 3,
  "status": "active",
  "series_id": "tesla-mandela-effects",
  "text_content": "500-1000 words of segment content...",
  "title": "INCOMPATIBLE TISSUE",
  "author": "gemini-2.5-flash",
  "created_at": "2026-01-15T12:00:00Z",
  "character_mentions": ["Nikola", "Dane", "Pasha"],
  "event_mentions": ["Dane's death"],
  "fact_mentions": ["nikola-age-at-dane-death"],
  "tags": ["opening", "flashback", "sensory"],
  "parent_version": 2
}
```

### Required Indexes (Create at collection setup)

```python
client.create_payload_index(collection_name="episodes", field_name="episode_id", field_schema="keyword")
client.create_payload_index(collection_name="episodes", field_name="status", field_schema="keyword")
client.create_payload_index(collection_name="episodes", field_name="version", field_schema="integer")
client.create_payload_index(collection_name="episodes", field_name="segment_id", field_schema="keyword")
```

### Versioning Rules

- Each version is a **distinct point** in Qdrant (point ID: `{episode_id}_{segment_id}_v{version}`)
- When new version created: previous version's `status` → `"superseded"`
- Only ONE point per `episode_id + segment_id` has `status: "active"`
- Query current: `filter: {must: [{key: "status", match: {value: "active"}}]}`
- Query history: filter by `episode_id + segment_id`, sort by `version DESC`

### Exact Query Patterns

```json
// Get active version of segment
{
  "filter": {
    "must": [
      {"key": "episode_id", "match": {"value": "003"}},
      {"key": "segment_id", "match": {"value": "scene-05"}},
      {"key": "status", "match": {"value": "active"}}
    ]
  }
}

// Get all versions of a segment (for history)
{
  "filter": {
    "must": [
      {"key": "episode_id", "match": {"value": "003"}},
      {"key": "segment_id", "match": {"value": "scene-05"}}
    ]
  }
}

// Get all active segments for an episode (to reconstruct full episode)
{
  "filter": {
    "must": [
      {"key": "episode_id", "match": {"value": "003"}},
      {"key": "status", "match": {"value": "active"}}
    ]
  }
}
```

### Segment Strategy

Episodes are chunked into segments (500-1000 words each):
- Enables granular editing without full episode re-writes
- Each segment can be independently versioned
- Segments can be recomposed into full episode for export

---

## 2. Canon Facts Collection

**Purpose**: Store extracted facts that constrain future episodes.

### Schema

```json
{
  "fact_id": "uuid",
  "fact_type": "character_age|relationship|event|terminology|lore_rule",
  "summary": "Nikola was 7 years old when Dane died",
  "episode_origin": "003",
  "origin_type": "EPISODE|DESIGN_BIBLE|INTERNET_RESEARCH",
  "status": "active",
  "series_id": "tesla-mandela-effects",
  "related_entities": ["Nikola", "Dane"],
  "character_id": "char-nikola-tesla",
  "confidence": 0.95,
  "source_text": "Nikola, seven years old at the time...",
  "created_at": "2026-01-15T12:00:00Z"
}
```

### Required Indexes

```python
client.create_payload_index(collection_name="canon_facts", field_name="episode_origin", field_schema="keyword")
client.create_payload_index(collection_name="canon_facts", field_name="fact_type", field_schema="keyword")
client.create_payload_index(collection_name="canon_facts", field_name="status", field_schema="keyword")
client.create_payload_index(collection_name="canon_facts", field_name="character_id", field_schema="keyword")
```

### Fact Extraction Prompt (Send FULL Episode)

```
Extract the following facts from the audio drama transcript below. Format your output as a JSON array of objects, with each object containing:
- "type": "character_age" | "character_relationship" | "event" | "terminology" | "lore_rule"
- "character_name" (if applicable)
- "related_entities" (array of character/entity names involved)
- "description" (the fact itself)
- "source_text" (exact quote from transcript, max 50 words)
- "confidence" (0.6-1.0)

EXTRACTION RULES:
- EXTRACT: Explicit facts ("Nikola was seven years old")
- EXTRACT: Implied facts with 0.6-0.8 confidence ("his older brother" implies sibling relationship)
- EXCLUDE: Subjective experiences ("The cold spread through him")
- EXCLUDE: Metaphors ("His heart was a stone")
- EXCLUDE: Transient sensations ("He felt dread")

Transcript:
[FULL 8,500-16,000 WORD TRANSCRIPT HERE]
```

### Fact Types

| Type | Example |
|------|---------|
| `character_age` | "Nikola was 7 in 1863" |
| `relationship` | "Dane is Nikola's brother" |
| `event` | "Dane died from horse kick" |
| `terminology` | "Đuka = Tesla family matriarch" |

### Precedence Rules (CRITICAL)

**HIGHEST to LOWEST priority:**

1. **Episode Canon** - Facts committed in published episodes (ALWAYS WINS)
2. **Design Bible** - Pre-defined series rules (superseded by episode canon)
3. **Approved Drafts** - Facts in approved but unpublished episodes
4. **Internet Research** - Historical facts (SUBSERVIENT TO ALL INTERNAL CANON)

### Contradiction Detection

1. Embed new fact's summary
2. Query `canon_facts` for similar vectors (threshold: 0.7)
3. Filter by `status: "active"` and matching `fact_type`
4. Send potential conflicts to LLM for analysis
5. Flag contradictions for human review - **NEVER auto-reject**

### Consistency Query Patterns

```json
// What do we know about Nikola? (character query)
{
  "filter": {
    "must": [
      {"key": "character_id", "match": {"value": "char-nikola-tesla"}},
      {"key": "status", "match": {"value": "active"}}
    ]
  }
}

// All facts from Episode 3 (episode query)
{
  "filter": {
    "must": [
      {"key": "episode_origin", "match": {"value": "003"}},
      {"key": "status", "match": {"value": "active"}}
    ]
  }
}

// Check for age contradictions before establishing new age fact
// Use vector search with the new fact summary, then filter results
{
  "filter": {
    "must": [
      {"key": "fact_type", "match": {"value": "character_age"}},
      {"key": "character_id", "match": {"value": "char-nikola-tesla"}},
      {"key": "status", "match": {"value": "active"}}
    ]
  }
}

// All terminology (for Caption Key deduplication)
{
  "filter": {
    "must": [
      {"key": "fact_type", "match": {"value": "terminology"}},
      {"key": "status", "match": {"value": "active"}}
    ]
  }
}
```

---

## 3. Episode Outputs Collection

**Purpose**: Store the three output files per episode.

### Schema

```json
{
  "output_id": "uuid",
  "episode_id": "003",
  "output_type": "CAPTION|TTS_VERSION|CAPTION_KEY",
  "version": 1,
  "text_content": "Full output file content...",
  "created_at": "2026-01-15T12:00:00Z",
  "metadata": {
    "word_count": 12500,
    "paragraph_count": 287,
    "derived_from_version": "uuid-of-caption-v1"
  }
}
```

### Output Types

| Type | Content | Example |
|------|---------|---------|
| `CAPTION` | Cultural spellings (source of truth) | Đuka, שָׁלוֹם, Ångström |
| `TTS_VERSION` | Romanized for ElevenLabs | Duka, shalom, Angstrom |
| `CAPTION_KEY` | New pronunciations only | {"original": "Đuka", "romanized": "DOO-kah"} |

### Caption Key Deduplication Process

1. Format new Caption Key as JSON array: `[{original, romanized}, ...]`
2. Query ALL existing `CAPTION_KEY` entries across all episodes
3. Extract all existing `original` values into a set
4. Filter proposed terms: keep only those NOT in existing set
5. Store final Caption Key with only truly new terms

---

## Editing Workflow

### Read → Edit → Write Cycle

```
1. FETCH CURRENT
   Query: episode_id + segment_id + is_current_version: true
   Result: Current segment text

2. EDIT
   - Human edits in UI, OR
   - Gemini edits via function calling

3. STORE NEW VERSION
   - Create new point with is_current_version: true
   - Update old point: is_current_version: false
   - Include change_summary in metadata

4. VIEW HISTORY (optional)
   Query: episode_id + segment_id (all versions)
   Sort by: created_at DESC

5. REVERT (optional)
   - Create new point with old content
   - Mark as current version
```

---

## Orchestration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Python Orchestrator                       │
│                 (gemini_qdrant_worker.py)                   │
│                                                              │
│   1. Read from Qdrant (fetch segments, canon, outputs)      │
│   2. Build prompts with fetched context                      │
│   3. Call Gemini API with tool definitions                   │
│   4. Dispatch function calls to Qdrant operations            │
│   5. Feed results back to Gemini                             │
│   6. Store final output to Qdrant                            │
│   7. Export to filesystem when complete                      │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ↓              ↓              ↓              ↓
    ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐
    │episodes │   │canon_facts│   │outputs  │   │Filesystem│
    └─────────┘   └──────────┘   └─────────┘   └──────────┘
```

---

## Implementation Order

### Phase 1: Core Collections
1. Create `episodes` collection with segment schema
2. Create `canon_facts` collection
3. Create `episode_outputs` collection

### Phase 2: Python Orchestrator
1. Build `gemini_qdrant_worker.py`
2. Define Qdrant operations as Gemini tools
3. Implement orchestration loop

### Phase 3: Workflows
1. Episode generation workflow
2. Editing sweep workflow
3. Fact extraction workflow
4. Output generation workflow (CAPTION → TTS → KEY)

### Phase 4: Export
1. Export from Qdrant to filesystem
2. Naming convention: `V[VERSION]_[EPISODE]_[NAME]_[TYPE].txt`
3. Directory structure per episode

---

*Schema designed based on research for 200+ episode series.*
*Segment-level versioning enables granular editing.*
*Precedence rules ensure canon consistency.*
