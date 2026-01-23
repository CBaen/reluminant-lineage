---
name: semantic-extractor
description: |
  Extract structured semantic data from documentary scripts for Qdrant storage.
  Uses 3 Gemini passes (different perspectives) + 1 Opus confirmation for 96-98% accuracy.

  Use when: (1) Extracting facts, lore, character states from episode scripts,
  (2) Populating Qdrant tesla_mandela_effects collection, (3) Building lore continuity
  for 200+ episode series.

  Content types extracted: historical_fact, lore_fact, character_state, open_mystery,
  proposed_question, revelation, forbidden_conclusion, used_imagery, used_sensory_language, relationship.

---

# Semantic Extractor V3

Extract structured narrative data from Tesla Mandela Effects documentary scripts.

## V3 Features

| Feature | Description |
|---------|-------------|
| **Fixed Voting** | Groups by TEXT, votes on classification separately (81% → <20% disagreement) |
| **Relationship Extraction** | Full entity_a/entity_b with direction, temporal context, evidence |
| **Deduplication** | Hash check + 0.90 threshold semantic similarity |
| **Flagged Review** | 0.90-0.95 similarity items flagged (may be contradictions) |
| **Parallel Embedding** | 32 concurrent workers for ~32x faster storage |
| **Batch Upsert** | 50 points per Qdrant call |
| **Episode Summaries** | Auto-generated metadata after extraction |
| **Sensory Vocabulary** | Tracks distinctive phrases with 50-episode decay |

## Pipeline Architecture

```
Episode Chunk
    ↓
Pass 1: Gemini (precise) → Account 1
    ↓ [5s delay]
Pass 2: Gemini (moderate) → Account 2
    ↓ [5s delay]
Pass 3: Gemini (exploratory) → Account 1
    ↓
V3 VOTING: Group by TEXT, vote on classification
    3/3 agree → Store (conf 0.95+)
    2/3 agree → Store majority (conf 0.85)
    1/3 or classification split → Opus tiebreaker
    ↓
DEDUPLICATION: Hash check → Semantic similarity
    >0.95 → Auto-merge (update episode_refs)
    0.90-0.95 → Flag for review (may be contradiction)
    <0.90 → Store as new
    ↓
PARALLEL EMBEDDING: 32 workers → Ollama nomic-embed-text
    ↓
BATCH UPSERT: 50 points/call → Qdrant tesla_mandela_effects
    ↓
EPISODE SUMMARY: Auto-generate metadata
    ↓
SENSORY SYNC: Track vocabulary for anti-cloning
```

## Quick Start

### Full Migration (Episodes 1 & 2)

```bash
# Dry-run first
python ~/.claude/skills/semantic-extractor/scripts/migrate-episodes.py --all --dry-run

# Run actual migration
python ~/.claude/skills/semantic-extractor/scripts/migrate-episodes.py --all
```

### Single Chunk Extraction

```bash
python ~/.claude/skills/semantic-extractor/scripts/extract-chunk.py \
    --episode 2 \
    --chunk-index 5 \
    --chunk-file /path/to/chunk.txt \
    --output results.json
```

### Store to Qdrant

```bash
# Save extraction to hub
python ~/.claude/skills/semantic-extractor/scripts/store-extractions.py \
    --save-extraction results.json

# Store episode with parallel embedding
python ~/.claude/skills/semantic-extractor/scripts/store-extractions.py \
    --store-episode 2
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `extract-chunk.py` | Run 3-pass Gemini extraction with V3 voting |
| `store-extractions.py` | Store to Qdrant with deduplication + parallel embedding |
| `reset-collection.py` | Backup/reset collection with V3 schema + indexes |
| `generate-episode-summary.py` | Auto-generate episode metadata |
| `sensory-vocabulary.py` | Manage sensory language tracking |
| `migrate-episodes.py` | Full V3 migration pipeline |
| `opus-batch-review.py` | Batch review disputed items (0.85 confidence) with Opus |

## Opus Batch Review (Post-Extraction QA)

After extraction, items with 2/3 Gemini agreement (0.85 confidence) need Opus review.

### Why Batched Review?

- **Problem**: 416 disputed items = 416 individual Opus calls = expensive + slow
- **Solution**: Batch 50 items per prompt = 9 batches total = ~95% cost reduction

### Workflow

```bash
# 1. Check current status
python ~/.claude/skills/semantic-extractor/scripts/opus-batch-review.py --status

# 2. Extract disputed items into batch files
python ~/.claude/skills/semantic-extractor/scripts/opus-batch-review.py --extract

# 3. Review each batch with Opus (via Claude Code Task tool or directly)
#    Input: batch_NNN_prompt.md
#    Output: Add "decisions" array to batch_NNN.json, save as batch_NNN_reviewed.json

# 4. Apply Opus decisions to Qdrant
python ~/.claude/skills/semantic-extractor/scripts/opus-batch-review.py --apply --batch-file batch_001_reviewed.json
```

### Batch File Structure

```
opus-review-batches/
├── batch_001.json           # Raw items from Qdrant
├── batch_001_prompt.md      # Prompt for Opus review
├── batch_001_reviewed.json  # Items + decisions array (after review)
├── batch_002.json
└── ...
```

### Decisions JSON Format

```json
{
  "decisions": [
    {"item": 1, "decision": "CONFIRM", "reasoning": "Correctly classified"},
    {"item": 2, "decision": "lore_fact", "reasoning": "Series-invented, not historical"}
  ],
  "items": [...]  // Original items from extraction
}
```

### Confidence Levels After Review

| Confidence | Meaning |
|------------|---------|
| 0.95+ (unanimous) | 3/3 Gemini agreement - no review needed |
| 0.95 (opus) | Opus reviewed and confirmed/corrected |
| 0.85 | 2/3 Gemini agreement - awaiting Opus review |

## Deduplication Commands

```bash
# Check if text is a duplicate
python ~/.claude/skills/semantic-extractor/scripts/store-extractions.py \
    --check-duplicate "Tesla's visions appeared during storms"

# Review flagged items (0.90-0.95 similarity)
python ~/.claude/skills/semantic-extractor/scripts/store-extractions.py \
    --review-flagged
```

## Sensory Vocabulary Commands

```bash
# Check if phrase is used
python ~/.claude/skills/semantic-extractor/scripts/sensory-vocabulary.py \
    --check "metallic tang of ozone" --episode 50

# Sync from episode extractions
python ~/.claude/skills/semantic-extractor/scripts/sensory-vocabulary.py \
    --sync --episode 2

# Show available for reuse (50+ episodes since last use)
python ~/.claude/skills/semantic-extractor/scripts/sensory-vocabulary.py \
    --available --episode 100
```

## Content Type Definitions (V3 Complete - 10 Types)

| Type | Key Question | Example |
|------|--------------|---------|
| `historical_fact` | "Can Google verify this?" | "The Carrington Event occurred September 1-2, 1859" |
| `lore_fact` | "Is this series-invented canon?" | "George Bliss received circular burns on his fingers" |
| `character_state` | "What does this character believe/feel?" | "Bliss felt his fingers were no longer his own" |
| `open_mystery` | "Would answering this destroy the horror?" | "What is using Bliss's fingers to touch the world?" |
| `proposed_question` | "Is this a question that MAY be answered later?" | "Why did the light target Nikola specifically?" |
| `revelation` | "Is this a major reveal/discovery?" | "Dane realized the sun had been replaced" |
| `forbidden_conclusion` | "Must this NEVER be answered definitively?" | "Is Nikola human or something else?" |
| `used_imagery` | "Is this a broader metaphor worth tracking?" | "the machinery of government" |
| `used_sensory_language` | "Is this a specific sensory construction?" | "water healing over a stone's splash" |
| `relationship` | "How do these entities connect?" | "Djuka → Nikola: protective (during infancy)" |

## The George Bliss Rule

Text presents characters as historical. They may NOT be verifiable.

**Default:** If a person/event cannot be confirmed via web search, classify as `lore_fact` with `appears_historical: true`.

**Only `historical_fact` for:**
- The Carrington Event (1859)
- Nikola Tesla (verified historical figure)
- Verified dates, places, documented events

## V3 Schema

Full schema: `WARDENCLYFFE/Editor_&_Writer_Rules/Qdrant_Schema_v3.md`

Key V3 additions:
- `text_hash` - SHA256 for deduplication
- `episode_refs` - Array of episodes where item appears
- `votes_for` - Classification consensus count
- `relationship_subjects` - Array index for relationship queries
- `entity_a`, `entity_b`, `direction`, `temporal_context`, `evidence` - Relationship fields

## Parallel Embedding Configuration

```python
PARALLEL_WORKERS = 32  # Concurrent Ollama requests
BATCH_SIZE = 50        # Points per Qdrant upsert
```

Approximate performance:
- Sequential: ~2 sec/item
- Parallel (32 workers): ~0.06 sec/item
- **~32x speedup**

## File Structure

```
~/.claude/skills/semantic-extractor/
├── SKILL.md                    # This file
├── sensory_vocabulary.json     # Tracked sensory phrases
├── migration_log.json          # Migration history
├── scripts/
│   ├── extract-chunk.py        # 3-pass extraction
│   ├── store-extractions.py    # Storage with dedup + parallel
│   ├── reset-collection.py     # Collection management
│   ├── generate-episode-summary.py
│   ├── sensory-vocabulary.py
│   ├── migrate-episodes.py
│   └── apply-opus-review.py    # Apply Opus tiebreaker results
└── extractions/
    ├── index.json              # Master index
    ├── flagged/                # Items needing review
    ├── summaries/              # Episode summaries
    ├── archived/               # 30-day retention
    └── episodes/
        ├── 001/
        │   ├── manifest.json
        │   ├── chunk-01-raw.txt
        │   ├── chunk-01.json
        │   └── ...
        └── 002/
            └── ...
```

## References

- V3 Schema: `WARDENCLYFFE/Editor_&_Writer_Rules/Qdrant_Schema_v3.md`
- V2 Schema (archived): `WARDENCLYFFE/Editor_&_Writer_Rules/Qdrant_Schema_v2.md`
- Episode 2 (gold standard): `WARDENCLYFFE/epsiodes/002 - THE LION VS THE WOLF/`
