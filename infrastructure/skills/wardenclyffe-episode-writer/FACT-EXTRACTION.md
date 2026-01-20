# Fact Extraction from Narrative Prose

**Source**: Research agent a03a301 (2026-01-15)
**Status**: READY FOR IMPLEMENTATION

---

## Recommended Approach: Hybrid Pipeline

```
Regex (Foundation) → spaCy (Linguistic) → Gemini LLM (Intelligence)
```

Each layer validates and enriches the previous layer.

| Layer | Purpose | Example |
|-------|---------|---------|
| **Regex** | Extract formatted data (dates, ages, codes) | `\b([0-9]{1,2})\s+years?\s+old\b` |
| **spaCy** | NER, coreference, dependency parsing | "Captain Eva" → char_eva_rostova |
| **Gemini** | Complex relationships, implied facts, confidence scoring | "gift from his sister" → infers sibling relationship |

---

## Decision Rules: What Is a Fact?

### EXTRACT (Facts)

| Type | Confidence | Example |
|------|------------|---------|
| **Explicit** | 0.9-1.0 | "Nikola was seven years old" |
| **Implied** | 0.6-0.89 | "his older brother" → sibling + relative age |

### EXCLUDE (Not Facts)

| Type | Example | Why Exclude |
|------|---------|-------------|
| Subjective experience | "The cold spread through him" | Sensation, not world state |
| Metaphor | "His heart was a stone" | Literary device |
| Transient sensation | "He felt dread" | Doesn't change world state |

---

## Schemas for Qdrant

### CHARACTER
```json
{
  "type": "character",
  "id": "char_nikola_tesla",
  "name": "Nikola Tesla",
  "aliases": ["Nikola", "Mr. Tesla"],
  "description": "Serbian inventor, 7 years old at brother's death",
  "associated_events": ["event_dane_death"],
  "text_embedding_source": "Nikola Tesla is a 7-year-old Serbian inventor",
  "confidence": 0.95,
  "source_episode": "001"
}
```

### ENTITY (objects, locations, organizations)
```json
{
  "type": "entity",
  "id": "entity_pasha_horse",
  "name": "Pasha",
  "entity_type": "horse",
  "description": "Family horse owned for 5 years",
  "associated_characters": ["char_nikola_tesla"],
  "text_embedding_source": "Pasha is a family horse owned for five years",
  "confidence": 0.92,
  "source_episode": "003"
}
```

### EVENT
```json
{
  "type": "event",
  "id": "event_dane_death",
  "name": "Dane's Death",
  "event_type": "tragedy",
  "description": "Nikola's brother Dane died from horse kick",
  "participants": ["char_nikola_tesla", "char_dane_tesla", "entity_pasha_horse"],
  "text_embedding_source": "Nikola's brother Dane died in 1863",
  "confidence": 0.98,
  "source_episode": "003"
}
```

### ATOMIC FACT
```json
{
  "type": "fact",
  "id": "fact_nikola_age_at_dane_death",
  "fact_statement": "Nikola was seven years old when Dane died",
  "subject_id": "char_nikola_tesla",
  "predicate": "age_at_event",
  "object": "7",
  "text_embedding_source": "Nikola was 7 years old when Dane died",
  "confidence": 0.95,
  "source_episode": "003"
}
```

### RELATIONSHIP
```json
{
  "type": "relationship",
  "id": "rel_nikola_dane_brothers",
  "relationship_type": "sibling",
  "source_id": "char_nikola_tesla",
  "target_id": "char_dane_tesla",
  "description": "Nikola and Dane are brothers",
  "text_embedding_source": "Nikola and Dane are brothers",
  "confidence": 0.98,
  "source_episode": "003"
}
```

---

## Confidence Scoring

| Range | Category | Action |
|-------|----------|--------|
| **0.9-1.0** | HIGH | Auto-canonize |
| **0.6-0.89** | MEDIUM | Human review queue |
| **< 0.6** | LOW | Discard or flag for clarification |

---

## Contradiction Detection

### Conflict Types

1. **Direct Attribute**: Same subject, same predicate, different values
   - "Nikola is 7" vs "Nikola is 5"

2. **Mutually Exclusive**: Contradictory states
   - `is_alive: true` AND `is_dead: true`

3. **Temporal Inconsistency**: Events violate causality
   - Event before character's birth

4. **Identity Conflict**: Same subject, different identities
   - "X is A" and "X is B"

### Detection Process

```pseudocode
FOR each new_fact:
  query_existing = Qdrant.search(subject_id, canonical: true)

  FOR each canon_fact in query_existing:
    IF same_predicate AND different_value:
      FLAG("Direct Attribute Conflict", new_fact, canon_fact)

    IF mutually_exclusive(new_fact, canon_fact):
      FLAG("Mutually Exclusive")

    IF temporal_violation(new_fact, canon_fact):
      FLAG("Temporal Inconsistency")

  RETURN conflicts → human review (do NOT auto-reject)
```

**Critical**: Never auto-reject contradictions. They may be intentional retcons or plot twists.

---

## Implementation Workflow

```
EPISODE INGESTION PIPELINE

1. PARSE TEXT
   └── Load 8,500-16,000 word episode

2. EXTRACT CANDIDATES (Regex → spaCy)
   ├── Regex: Dates, numbers, formatted data
   ├── spaCy: NER, coreference, entities
   └── Output: Annotated text + entity mentions

3. LLM EXTRACTION (Gemini)
   ├── Input: Annotated text + coreference chains
   ├── Prompt: "Extract facts about characters, relationships, events"
   ├── Output: Structured facts with confidence scores
   └── Filter: Exclude narrative elements

4. CLASSIFY FACT TYPES
   ├── Character facts (age, traits)
   ├── Entity facts (ownership, properties)
   ├── Event facts (what, when, where, who)
   └── Relationship facts (sibling, owns, etc.)

5. ASSIGN CONFIDENCE
   ├── Explicit + Regex/spaCy → 0.95+
   ├── Implied + LLM inference → 0.65-0.85
   └── Narrative/ambiguous → 0.3-0.6 (EXCLUDE)

6. CHECK CONTRADICTIONS
   ├── Query Qdrant for facts about same subject
   ├── Compare predicates/values
   └── Flag conflicts → human review queue

7. CANON MANAGEMENT
   ├── >= 0.9: AUTO-ADD
   ├── 0.6-0.89: HUMAN REVIEW
   └── < 0.6: DISCARD

8. UPDATE CANON DATABASE
   └── Commit to Qdrant with audit trail
```

---

## Tech Stack

| Component | Tool |
|-----------|------|
| NER + Coreference | spaCy |
| LLM Intelligence | Gemini API |
| Vector Storage | Qdrant |
| Validation | Custom contradiction rules |
| Canon Review | Human-in-the-loop dashboard |

---

## Key Insights

1. **LLM is essential for fiction** - Regex and spaCy miss implied relationships
2. **Hybrid minimizes hallucinations** - Each layer validates the previous
3. **Confidence scoring prevents drift** - Not all facts are equally reliable
4. **Contradictions need humans** - Auto-rejection would break intentional retcons
5. **Rich schemas enable queries** - `type`, `subject_id`, `text_embedding_source`

---

*Designed for 200+ episode series where canon consistency is critical.*
