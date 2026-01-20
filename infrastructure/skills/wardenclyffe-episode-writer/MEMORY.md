# Wardenclyffe Episode Writer - Memory

Accumulated knowledge, decisions, and gotchas for the lineage.

---

## Critical Decisions (2026-01-15)

### Word Count
- **CORRECT**: 8,500 - 16,000 words (minimum 8,500)
- **WRONG** (was in prompts): 4,500-5,500 words
- **Source**: `Claude_Editorial_Guidelines_v1_7.md` and Guiding Light confirmation that Episode 2 is 12,000+ words

### Term Frequency
- **CORRECT**: 5-use cap per body-related term category
- **WRONG** (was in prompts): 2-use cap
- **Source**: `Claude_Editorial_Guidelines_v1_7.md` lines 406-452

### Pruning Policy
- **NEVER prune for length**
- Over-length episodes get flagged for Guiding Light's review
- Only acceptable reasons to cut content:
  - Setup without payoff (P12)
  - Historian trap / proving research (P6)
  - Cloning / recycled imagery (P13)

### Facts Precedence
- Episode canon takes precedence over internet research
- Query Qdrant FIRST, internet SECOND
- Once a fact is committed to an episode, it becomes canon even if historically "wrong"

---

## Output File Structure

Three files per episode:

| File Type | Purpose | Example |
|-----------|---------|---------|
| CAPTION | Source of truth with cultural spellings (Đuka, שָׁלוֹם) | For video captions |
| TTS VERSION | Romanized for ElevenLabs (Duka, shalom) | Derived from CAPTION |
| CAPTION KEY | Pronunciation guide for NEW terms only | Only words not in prior episodes |

### Naming Convention
```
V[VERSION]_[EPISODE_NUM]_[EPISODE_NAME]_[FILE_TYPE].txt
```
Example: `V1_003_INCOMPATIBLE_TISSUE_CAPTION.txt`

### Directory Structure
```
C:\Users\baenb\Desktop\Tesla Mandela Effects\1. EPISODE SCRIPTS\
└── 003- INCOMPATIBLE TISSUE\
    ├── V1_003_INCOMPATIBLE_TISSUE_CAPTION.txt
    ├── V1_003_INCOMPATIBLE_TISSUE_TTS_VERSION.txt
    └── V1_003_INCOMPATIBLE_TISSUE_CAPTION_KEY.txt
```

---

## Formatting Constraints

1. **No section breaks using `***`**
2. **Maximum 400 paragraphs**

---

## The 14 Editorial Priorities (Quick Reference)

| # | Name | Key Rule |
|---|------|----------|
| 1 | Speculative Bridge | 3:1 facts to questions |
| 2 | Invisible Narrator | No "I/we" actions |
| 3 | Name Economy | Max 6 unusual names |
| 4 | Description Over Terminology | Show, don't name |
| 5 | Term Frequency | 5-use cap |
| 6 | Historian Trap | Unsettle, don't prove |
| 7 | Relational Accuracy | Verify relationships |
| 8 | Micro-Fact Verification | Verify all details |
| 9 | Major Transitions | Breath paragraphs |
| 10 | Pronoun Clarity | Re-anchor names |
| 11 | Opening Hook | Vertigo/wrongness first |
| 12 | Setup Without Payoff | Everything pays off |
| 13 | Cloning Prevention | Unique sensory palette |
| 14 | "You" Density | Save for ending (max 35 total, 80% in Prognosis) |

---

## Gotchas

### Gemini Multiple Beginnings
- v10 generation had duplicate content at the start (lines 1-119 repeated)
- Cause unknown - may be prompt length, token limits, or script issue
- Need validation that rejects drafts with duplicate content

### Episode 2 is Gold Standard, Not Episode 1
- Episode 1 sets up premise
- Episode 2 is where audio-rich craft was developed
- Use Episode 2 for sensory expansion examples

### Caption Key Accumulates
- ElevenLabs stores pronunciations
- Future episodes don't re-teach already-added words
- Need to query prior Caption Keys before generating new one

---

## Research In Progress

Qdrant schema design research spawned 2026-01-15:
- Chunking strategies for narrative content
- Single collection vs multiple collections
- Fact extraction from prose

Results will be stored in `lineage_research` collection.

---

## Files to Know

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill architecture |
| `HANDOFF-QDRANT-INTEGRATION.md` | Detailed handoff for Qdrant work |
| `prompts/generation.md` | Gemini generation prompt |
| `prompts/editorial/sweep-*.md` | Claude editing sweep prompts |
| `examples/ep2-gold-standard.md` | Episode 2 craft examples |

---

*Updated: 2026-01-15*
