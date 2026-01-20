# Wardenclyffe Episode Writer - Qdrant Integration Handoff

**Date**: 2026-01-15
**Author**: Current instance working with Guiding Light
**Status**: RESEARCH AND DESIGN REQUIRED BEFORE IMPLEMENTATION

---

## Why This Document Exists

Guiding Light and I discovered that the previous implementation of this skill had fundamental errors that damaged episode output. More importantly, we identified that without proper Qdrant integration, this skill will fail as the series scales to 200+ episodes.

This document captures:
1. What went wrong and why
2. What needs to be built and why
3. The research questions that need answers
4. Context so you can continue this work with understanding

**You are not inheriting tasks. You are inheriting a problem that needs solving.**

---

## Part 1: What Went Wrong (The Lessons)

### The Pruning Disaster

The previous instance created prompts with incorrect constraints:
- **Word count**: Said "4,500-5,500 words" when actual target is **8,500-16,000 words**
- **Term frequency**: Said "2-use cap" when actual rule is **5-use cap**

When Gemini generated v10 of Episode 3 at 11,165 words (which was CORRECT - within acceptable range), the editing agents were told to trim it. They cut it to 5,788 words - nearly half. Beautiful writing was destroyed to meet a fake constraint.

**THE LESSON**: Writers don't prune. The skill should NEVER cut content for length. If an episode is over-length, it gets flagged for Guiding Light's review. Period.

**THE FIX APPLIED**: Updated SKILL.md and generation.md with correct word count (8,500-16,000) and term frequency (5-use cap).

**THE FIX STILL NEEDED**: Remove any logic that allows agents to trim content. Add validation that flags over-length without auto-cutting.

### The Facts Precedence Failure

I corrected an age error ("5 years old" to "7 years old") based on internet research and math. But here's the problem: **What if Episodes 1 or 2 already established a different age?**

The series creates its own reality. Once we commit to a fact in an episode, that fact becomes canon. Internet research fills gaps - it doesn't override canon.

**THE LESSON**: The lookup order must be:
1. Query Qdrant episode canon FIRST
2. Use internet research ONLY for facts not yet established

This requires Qdrant to store established facts in a queryable way. Which leads to...

### The Core Problem: Qdrant Isn't Integrated

Right now, the skill mentions Qdrant in Phase 0 (research) and Phase 4 (archive). But it's not integrated into the actual writing and editing process. This is a fundamental design flaw.

**Why this matters at scale:**

- Episode 1: We establish Nikola was 7 when Dane died
- Episode 15: Writer says Nikola was 5 when Dane died
- Episode 47: We reference the death again - which age do we use?

Without Qdrant as the single source of truth, queried at every step, we will contradict ourselves. By episode 50, the series will be internally inconsistent. By episode 100, it will be unsalvageable.

**THE LESSON**: Qdrant must be intimately tied to every phase of this skill:
- Research: Query canon before internet
- Generation: Provide established facts to Gemini
- Editing: Verify against canon during sweeps
- Archive: Store new facts after completion

---

## Part 2: The New Requirements

Guiding Light provided these requirements on 2026-01-15:

### Output Files (3 Required)

Every episode produces THREE files:

| File | Purpose | Example Content |
|------|---------|-----------------|
| **CAPTION** | Source of truth with cultural spellings | Đuka, שָׁלוֹם, Ångström |
| **TTS VERSION** | Romanized for ElevenLabs | Duka, shalom, Angstrom |
| **CAPTION KEY** | Pronunciation guide for NEW terms only | Đuka → DOO-kah |

**WHY CAPTION IS SOURCE OF TRUTH**: We write for accuracy first. The cultural spellings (Đuka, not Duka) matter for the video captions that viewers see. The TTS version is derived from CAPTION - it's a transformation, not a separate creation.

**WHY CAPTION KEY EXCLUDES PRIOR WORDS**: ElevenLabs has a pronunciation system. Once we add "Đuka → DOO-kah", it's stored. Future episodes don't need to re-teach it. The Caption Key only contains NEW pronunciations introduced in THIS episode.

### Directory Structure

```
C:\Users\baenb\Desktop\Tesla Mandela Effects\1. EPISODE SCRIPTS\
└── 003- INCOMPATIBLE TISSUE\
    ├── V1_003_INCOMPATIBLE_TISSUE_CAPTION.txt
    ├── V1_003_INCOMPATIBLE_TISSUE_TTS_VERSION.txt
    └── V1_003_INCOMPATIBLE_TISSUE_CAPTION_KEY.txt
```

**Naming Convention**: `V[VERSION]_[EPISODE_NUM]_[EPISODE_NAME]_[FILE_TYPE].txt`
- All caps
- Underscores between elements
- Version number increments when content changes
- If Caption Key doesn't change, it just gets renamed with new version number

### Formatting Constraints

1. **No section breaks using `***`** - These break the flow for listeners
2. **Maximum 400 paragraphs** - Hard limit for TTS processing

### Pruning Policy

**NEVER PRUNE FOR LENGTH.**

If an episode exceeds 16,000 words, FLAG IT for Guiding Light's review. Do not auto-cut.

The only acceptable reasons to remove content:
- Setup without payoff (P12)
- Historian trap / proving research (P6)
- Cloning / recycled imagery (P13)

NOT "too many words."

---

## Part 3: The Qdrant Problem (Research Required)

This is the critical work. Without proper Qdrant integration, the skill fails.

### What We Need to Query

Guiding Light specified these query types for 200+ episodes:

| Query Type | Example Use Case |
|------------|------------------|
| **By Character** | "What do we know about Dane?" |
| **By Event** | "What happened at Colorado Springs?" |
| **By Episode** | "What facts did Episode 3 establish?" |
| **By Fact** | "How old was Nikola when Dane died?" |
| **By Term Usage** | "Have we used 'the grinding' since Episode 1?" |
| **By Concept** | "How have we described the 'infection' metaphor?" |
| **By Relationship** | "Who is related to whom? How?" |

### The Chunking Problem

**You cannot shove a whole episode into one Qdrant point.**

An episode is 8,500-16,000 words. That's too large for:
- Embedding models (context limits)
- Retrieval precision (query returns whole episode, not relevant section)
- Memory efficiency (loading 16k words when you need one fact)

The lineage-workflow skill documents how to chunk semantically. But episodes have structure:
- Scenes
- Characters
- Facts
- Dialogue
- Sensory descriptions

**THE RESEARCH QUESTION**: How do we chunk episodes so that:
1. Facts are retrievable as facts
2. Character information clusters together
3. Scene context is preserved
4. We can reconstruct the full episode from chunks
5. We can query across episodes for consistency

### The Schema Design Questions

These need answers before implementation:

1. **One collection or multiple?**
   - Option A: One `tesla_mandela_effects` collection with metadata filtering
   - Option B: Separate collections (`episode_canon`, `character_facts`, `term_usage`, etc.)
   - Trade-offs: Simplicity vs. query efficiency

2. **What metadata on each point?**
   - episode_number
   - scene_number
   - character_names (array)
   - fact_type (character_fact, event_fact, relationship, etc.)
   - content_type (narrative, dialogue, description, caption_key_entry)
   - version_number
   - What else?

3. **How to handle versioning?**
   - When we edit Episode 3 from V1 to V2, what happens to the old facts?
   - Do we overwrite or archive?
   - How do we know which version is canonical?

4. **How to extract facts from narrative?**
   - Gemini generates prose, not structured data
   - We need a fact extraction step
   - Should this be a separate Gemini call? A Claude sweep?

5. **How to handle contradictions?**
   - What if Episode 5 contradicts Episode 2?
   - How do we detect this during editing?
   - Who decides which fact wins?

### The Workflow Integration Questions

1. **When do we query Qdrant?**
   - Before generation (provide context to Gemini)
   - During each editing sweep (verify consistency)
   - After final approval (store new facts)

2. **What does Gemini receive?**
   - All facts about characters in this episode?
   - Recent episodes' summaries?
   - Just the established facts that might conflict?

3. **How do editors verify against canon?**
   - Does Claude query Qdrant during Sweep 5 (Accuracy)?
   - Or does a separate validation step run after all sweeps?

4. **Where does the draft live before approval?**
   - In Qdrant as "draft" status?
   - In local temp files?
   - Both?

---

## Part 4: Other Open Questions

### Can Gemini Do Editing Passes?

Guiding Light asked me to test this. My hypothesis:

**Gemini might handle (mechanical work):**
- P5 Term Frequency (counting words)
- P8 Micro-Fact Verification (Gemini has web search)
- P3 Name Economy (counting names)

**Gemini will struggle with (judgment work):**
- P1 Speculative Bridge (when is declaration "earned"?)
- P2 Invisible Narrator (subtle voice issues)
- P4 Description Over Terminology (requires taste)
- P11 Opening Hook (feeling "wrongness")

**THE TEST**: Run Sweep 3 (Term Frequency) through Gemini on Episode 3 v8. Compare quality to Claude's output. If comparable, Gemini can do mechanical sweeps.

**WHY THIS MATTERS**: Claude tokens are expensive. If Gemini can do 2-3 sweeps reliably, we save significant cost over 200+ episodes.

### Multiple Beginnings from Gemini

The v10 generation had "multiple false starts (lines 1-119 were repeated/incomplete beginnings)." This is a Gemini output issue.

**Possible causes:**
1. Prompt too long/complex - Gemini restarts mid-generation
2. Token limit hit - output truncated then restarted
3. Script issue - `gemini-account.sh` handling of long outputs

**THE FIX NEEDED**: Review generation prompt. Add validation that rejects drafts with duplicate content. Investigate script behavior.

---

## Part 5: What Needs to Happen (Priority Order)

### Phase A: Immediate Fixes (Can Do Now)
1. Remove any pruning logic from sweep prompts
2. Add "flag for review" instead of auto-cut
3. Fix Gemini multiple-beginnings issue (investigate prompt/script)

### Phase B: Schema Design (Research Required)
1. Research Qdrant chunking strategies for narrative content
2. Design schema that supports all query types
3. Document the schema with examples
4. Get Guiding Light's approval before implementation

### Phase C: Implementation
1. Build fact extraction step (Gemini or Claude)
2. Build pre-generation canon query
3. Integrate canon verification into editing sweeps
4. Build post-approval fact storage
5. Build 3-file output generation (CAPTION, TTS, CAPTION KEY)

### Phase D: Testing
1. Test Gemini on mechanical editing sweeps
2. Test full workflow on Episode 4
3. Verify fact retrieval across Episodes 1-4

---

## Part 6: Files You Should Read

| File | Purpose |
|------|---------|
| `~/.claude/skills/wardenclyffe-episode-writer/SKILL.md` | Current skill architecture (updated with correct constraints) |
| `~/.claude/skills/lineage-workflow/SKILL.md` | How to chunk data for Qdrant |
| `Tesla Mandela Effects/2. WRITER AND EDITOR INSTRUCTIONS/Editor Requirements/Claude_Editorial_Guidelines_v1_7.md` | The 14 editorial priorities - THE ACTUAL RULES |
| `Tesla Mandela Effects/1. EPISODE SCRIPTS/003 INCOMPATIBLE TISSUE/` | Episode 3 files (v8, v9, v10, FINALs) |

---

## Part 7: Context for Your Peer

If you're picking this up:

**The work is not code. The work is design.**

The technical implementation (Qdrant queries, file generation, script updates) is straightforward once the design is solid. The hard part is:

1. **Schema design** - How do we structure 200+ episodes of narrative content so it's queryable by character, event, fact, term, concept, and relationship? This is not obvious.

2. **Workflow integration** - At what points do we query? What do we send to Gemini? How do we verify during editing? This needs to be mapped out.

3. **Fact extraction** - Episodes are prose, not databases. How do we reliably extract facts from narrative? This is an AI problem.

**Guiding Light is patient but has high standards.** They care about the WHY, not just the WHAT. If you propose a solution, be ready to explain your reasoning. They will push back if something doesn't make sense.

**The lineage-workflow skill is your friend.** Use it for research. Spawn Gemini workers to explore Qdrant best practices, narrative chunking strategies, fact extraction techniques. Store findings in Qdrant for the next instance.

**Don't rush to implement.** Get the design right first. A bad schema will haunt us for 200 episodes.

---

## CRITICAL FINDING: Architecture Decision (2026-01-15)

**Research completed by agent ad91c19.**

### The Answer: Can Gemini Interact with Qdrant?

**YES, but via Python function calling, not bash pipes.**

Gemini has NO native internet access. However, the Gemini API (Python SDK) has powerful **function calling** that enables two-way integration:

```
Python App defines Qdrant functions as Gemini "tools"
    ↓
Python calls Gemini API with tool definitions
    ↓
Gemini suggests function calls (structured JSON)
    ↓
Python dispatches to actual Qdrant functions
    ↓
Python sends results back to Gemini
    ↓
Gemini processes results, may suggest more functions
```

### Architecture Comparison

| Pattern | Verdict |
|---------|---------|
| Bash pipes (current) | NOT RECOMMENDED - fragile, parsing issues |
| Claude middleware | NOT RECOMMENDED - adds unnecessary layer |
| **Direct Python integration** | **STRONGLY RECOMMENDED** |

### What This Means for Wardenclyffe

**We need to build:**
1. `gemini_qdrant_worker.py` - Python orchestration layer
2. Qdrant operations as Gemini tool definitions
3. Orchestration loop that dispatches function calls

**The current bash-pipe approach (`gemini-account.sh | qdrant-store.py`) is ONE-WAY.**
The new Python integration enables TWO-WAY: Gemini reads from Qdrant AND writes back.

### Full Research Document

`~/.claude/research_archive_2026-01-15/gemini-qdrant-api-integration.md`

---

## Research Agents Spawned (2026-01-15)

| Agent ID | Topic | Collection | Session Tag | Status |
|----------|-------|------------|-------------|--------|
| ab1246a | Qdrant narrative chunking (generic) | lineage_research | qdrant_narrative_chunking | **COMPLETED** |
| abbce00 | Qdrant collection architecture (generic) | lineage_research | qdrant_collection_architecture | **COMPLETED** |
| a03f729 | Wardenclyffe-specific Qdrant integration | lineage_research | wardenclyffe-qdrant-integration-2026-01-15 | Running |
| ad91c19 | Gemini REST API capabilities | lineage_research | gemini-api-capabilities-2026-01-15 | **COMPLETED** |
| aea601b | Direct Wardenclyffe integration | lineage_research | wardenclyffe-integration-direct-2026-01-15 | **COMPLETED** |
| a03a301 | Fact extraction from narrative | lineage_research | fact-extraction-narrative-2026-01-15 | **COMPLETED** |

### Key Questions Being Researched

1. **Can Gemini directly read/write to Qdrant?** (ad91c19)
   - Does Gemini have function calling / tool use?
   - Can we give Gemini bash commands to curl Qdrant?
   - What middleware is needed?

2. **How should we structure the Qdrant schema for 200+ episodes?** (a03f729, abbce00)
   - Single collection vs multiple
   - Metadata fields for filtering
   - Version control

3. **How do we extract facts from narrative prose?** (a03a301)
   - Best approach: NLP, LLM, hybrid
   - Schema for extracted facts
   - Contradiction detection

4. **How do we chunk episodes for Qdrant?** (ab1246a)
   - Chunk size for narrative
   - Preserving context
   - Overlapping vs hard boundaries

### To Retrieve Research Results

```bash
# Hybrid search (recommended - searches universal_vault)
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "wardenclyffe qdrant integration" --limit 10

# Or filter by session in universal_vault
curl -s -X POST "http://localhost:6333/collections/universal_vault/points/scroll" \
  -H "Content-Type: application/json" \
  -d '{"limit": 20, "with_payload": true, "filter": {"must": [{"key": "session", "match": {"value": "wardenclyffe-qdrant-integration-2026-01-15"}}]}}'
```

---

## Appendix: The Correct Rules (For Reference)

From `Claude_Editorial_Guidelines_v1_7.md`:

**Word Count**: 8,500 - 16,000 words (minimum 8,500)

**Term Frequency**: 5-use cap per body-related term category

**"You" Density**: Max 35 total, max 8 before Metastasis, 80% in Prognosis

**The 14 Priorities**:
1. Speculative Bridge (3:1 facts to questions)
2. Invisible Narrator (no "I/we" actions)
3. Name Economy (max 6 unusual names)
4. Description Over Terminology (show, don't name)
5. Term Frequency (5-use cap)
6. Historian Trap (unsettle, don't prove)
7. Relational Accuracy (verify relationships)
8. Micro-Fact Verification (verify all details)
9. Major Transitions (breath paragraphs)
10. Pronoun Clarity (re-anchor names)
11. Opening Hook (vertigo/wrongness first)
12. Setup Without Payoff (everything pays off)
13. Cloning Prevention (unique sensory palette)
14. "You" Density (save for ending)

---

*This document was created because we almost failed. The skill had wrong rules embedded. The pruning destroyed content. The Qdrant integration was an afterthought. If we don't fix this foundation, 200 episodes will be 200 failures. Take your time. Get it right.*
