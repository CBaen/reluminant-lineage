---
name: semantic-extractor
description: |
  Extract structured semantic data from documentary scripts for Qdrant storage.
  Uses 3 Gemini passes (different perspectives) + 1 Opus confirmation for 96-98% accuracy.

  Use when: (1) Extracting facts, lore, character states from episode scripts,
  (2) Populating Qdrant tesla_mandela_effects collection, (3) Building lore continuity
  for 200+ episode series.

  Content types extracted: historical_fact, lore_fact, character_state, open_mystery,
  proposed_question, used_imagery, used_sensory_language, episode_term_usage, relationship.
---

# Semantic Extractor

Extract structured narrative data from Tesla Mandela Effects documentary scripts.

## Pipeline Architecture

```
Episode Chunk
    ↓
Pass 1: Gemini (temp 0.1, precise) → Account 1
    ↓ [5s delay]
Pass 2: Gemini (temp 0.3, moderate) → Account 2
    ↓ [5s delay]
Pass 3: Gemini (temp 0.5, exploratory) → Account 1
    ↓
COMPARE: 3/3 agree → Store (conf 0.95+)
         2/3 agree → Store majority (conf 0.85), flag dissent
         0/3 agree → Opus tiebreaker
    ↓
Opus: Fact/fiction verification + narrative reasoning
    ↓
Store to Qdrant tesla_mandela_effects
```

## Execution

### Step 1: Prepare the chunk

Get chunk text from Qdrant or file. Target: 500-800 words.

### Step 2: Run the extraction script

```bash
# Run all 3 passes with automatic voting
python ~/.claude/skills/semantic-extractor/scripts/extract-chunk.py \
    --episode 2 \
    --chunk-index 5 \
    --chunk-file /path/to/chunk.txt \
    --output results.json
```

Or with inline text:
```bash
python ~/.claude/skills/semantic-extractor/scripts/extract-chunk.py \
    --episode 2 \
    --chunk-index 5 \
    --chunk-text "The letter was rediscovered..."
```

The script automatically:
1. Runs Pass 1 (Precise) via Gemini CLI
2. Waits 5 seconds (rate limiting)
3. Runs Pass 2 (Moderate) via Gemini CLI
4. Waits 5 seconds
5. Runs Pass 3 (Exploratory) via Gemini CLI
6. Compares all extractions and votes

### Step 3: Compare and vote

```python
# Pseudocode for voting logic
def compare_extractions(pass1, pass2, pass3):
    results = []
    all_items = merge_by_text_similarity(pass1, pass2, pass3)

    for item in all_items:
        agreement = count_passes_that_found(item)

        if agreement == 3:
            item.confidence = 0.95
            item.needs_opus = False
        elif agreement == 2:
            item.confidence = 0.85
            item.dissent = get_dissenting_view(item)
            item.needs_opus = False
        else:  # All different
            item.needs_opus = True

    return results
```

### Step 4: Opus confirmation (when needed)

Run Opus on:
1. Items where all 3 passes disagreed
2. ALL `historical_fact` classifications (verify if truly verifiable)
3. Borderline `lore_fact` vs `historical_fact` cases

Opus prompt template:
```
You are the TIEBREAKER for narrative extraction.

CONTEXT: Tesla Mandela Effects is a documentary series blending real history
with invented lore. George Bliss-style characters may APPEAR historical but
are unverifiable - default to lore_fact unless independently confirmable.

CRITICAL: The 1859 Carrington Event is REAL (historical_fact).
George Bliss is UNVERIFIABLE (lore_fact).

DISAGREEMENT TO RESOLVE:
{items_needing_resolution}

Apply rigorous narrative reasoning. Return final classification with reasoning.
```

### Step 5: Store to Qdrant

```bash
# Store validated extractions
python ~/.claude/scripts/qdrant-store-gemini.py \
    --collection tesla_mandela_effects \
    --topic "ep{episode_number}-chunk{chunk_index}" \
    --session "SemanticExtractor" \
    < validated_extractions.json
```

## Content Type Definitions

| Type | Key Question | Example |
|------|--------------|---------|
| `historical_fact` | "Can Google verify this?" | "The Carrington Event occurred September 1-2, 1859" |
| `lore_fact` | "Is this series-invented canon?" | "George Bliss received circular burns on his fingers" |
| `character_state` | "What does this character believe/feel?" | "Bliss felt his fingers were no longer his own" |
| `open_mystery` | "Would answering this destroy the horror?" | "What is using Bliss's fingers to touch the world?" |
| `used_sensory_language` | "Should this metaphor not repeat?" | "water healing over a stone's splash" |

## The George Bliss Rule

Text presents characters as historical. They may NOT be verifiable.

**Default:** If a person/event cannot be confirmed via web search, classify as `lore_fact` with `appears_historical: true`.

**Only `historical_fact` for:**
- The Carrington Event (1859)
- Nikola Tesla (verified historical figure)
- Verified dates, places, documented events

## References

- Full schema: `Editor_&_Writer_Rules/Qdrant_Schema_v2.md`
- Research findings: `~/.claude/research/hot/llm-extraction-accuracy.md`
- Episode 2 (gold standard): `epsiodes/002 - THE LION VS THE WOLF/V8 002- THE LION VS THE WOLF.txt`
