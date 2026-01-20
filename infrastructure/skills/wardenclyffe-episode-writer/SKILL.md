---
name: wardenclyffe-episode-writer
description: Generate Tesla Mandela Effects episodes using Gemini for generation and Claude for editing. Episode 2 is the craft template. Uses 16 single-responsibility agents.
allowed-tools: Task, TodoWrite, Bash, Read, Edit, Write
---

# Wardenclyffe Episode Writer

Claude Code IS the Writer's Room. Gemini generates. Claude edits via 16 single-responsibility agents.

---

## The Architecture (v2: 16-Agent Pipeline)

```
Research (Gemini subagent → Qdrant)
    ↓
Generate (Gemini subagent → full episode draft)
    ↓
Phase 1: MECHANICAL AUDITS
    01-deduplicator → 02-anchor → 03-term-counter → 04-you-density
    ↓
Phase 2: STRUCTURAL EDITS
    05-opening-hook → 06-transitions → 07-payoff-tracker
    ↓
Phase 3: VOICE EDITS
    08-bridge-balancer → 09-narrator-eraser → 10-jargon-killer → 11-dread-enforcer
    ↓
Phase 4: ACCURACY CHECKS
    12-relation-verifier → 13-fact-checker
    ↓
Phase 5: FINAL POLISH
    14-name-economist → 15-clone-detector → 16-sensory-expander
    ↓
Validate (App analyzers OR manual review)
    ↓
Save to Qdrant for lore continuity
```

---

## Why 16 Agents Instead of 5 Sweeps

The old 5-sweep system bundled priorities together:
- Sweep 3 handled P4, P5, AND P13 together
- Sweep 4 handled P3, P10, AND P14 together

**The problem:** When an agent tries to follow 3 rules simultaneously, rules interact and conflict. Fixing one violation can create another. Episode 3 went through 8+ drafts with no resolution.

**The solution:** Each agent has ONE job. 100-150 lines of focused instructions. No priority can step on another.

---

## The 16 Agents

| Pass | Agent | Priority | ONE JOB |
|------|-------|----------|---------|
| 01 | `deduplicator` | NEW | Remove repeated phrases/concepts |
| 02 | `anchor` | P10 | Fix pronoun avalanches, add name anchors |
| 03 | `term-counter` | P5 | Enforce 5-use cap, flag for agent 16 |
| 04 | `you-density` | P14 | Move "you" to ending |
| 05 | `opening-hook` | P11 | Ensure first sentence creates vertigo |
| 06 | `transitions` | P9 | Add breath paragraphs at jumps |
| 07 | `payoff-tracker` | P12 | Ensure all setups pay off |
| 08 | `bridge-balancer` | P1 | Enforce 3:1 fact-to-question ratio |
| 09 | `narrator-eraser` | P2 | Remove narrator identity leaks |
| 10 | `jargon-killer` | P4 | Replace terminology with sensation |
| 11 | `dread-enforcer` | P6 | Convert proof to unsettling |
| 12 | `relation-verifier` | P7 | Verify relationships are accurate |
| 13 | `fact-checker` | P8 | Verify ages, dates, distances |
| 14 | `name-economist` | P3 | Reduce names to ≤6 |
| 15 | `clone-detector` | P13 | Flag recycled Episode 1/2 imagery |
| 16 | `sensory-expander` | P4+ | Transform violations into micro-stories |

**Agent docs:** `prompts/editorial/agents/[NN]-[name].md`
**Orchestration guide:** `prompts/editorial/agents/ORCHESTRATION.md`

---

## Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `{{EPISODE_NUM}}` | Yes | Episode number |
| `{{TITLE}}` | Yes | Episode title |
| `{{HISTORICAL_PERIOD}}` | Yes | Era/event being covered |
| `{{OUTLINE}}` | Yes | Scene-by-scene outline with emotional beats |
| `{{COLLECTION}}` | No | Qdrant collection (default: `tesla_mandela_effects`) |

---

## Phase 0: Research

**Spawn a Haiku supervisor to research historical context.**

```
Task tool:
  subagent_type: "general-purpose"
  model: "haiku"
  prompt: [USE RESEARCH TEMPLATE BELOW]
```

### Research Template

```
You are a Research Supervisor for Tesla Mandela Effects Episode {{EPISODE_NUM}}: "{{TITLE}}"

TASK 1: Query existing lore
python ~/.claude/scripts/qdrant-semantic-search.py --collection "tesla_mandela_effects" --query "{{HISTORICAL_PERIOD}}" --limit 5 --json

TASK 2: Query episode canon (if episodes exist)
python ~/.claude/scripts/qdrant-semantic-search.py --collection "episode_canon" --query "characters relationships established facts" --limit 10 --json

TASK 3: Research new historical context via Gemini
~/.claude/scripts/gemini-account.sh 1 'You are researching for an audio drama episode.

HISTORICAL PERIOD: {{HISTORICAL_PERIOD}}
PERSPECTIVE: audio-first storytelling (listener cannot go back, every sentence must land)

Research comprehensively but focus on:
1. Sensory details of the era (what did it smell like, sound like, feel like?)
2. Specific names, dates, relationships that can be verified
3. Unsettling details that create dread, not education
4. Elements that can be presented as mystery, not facts

Return structured JSON with:
- Verified facts (with sources)
- Sensory details by category (visual, auditory, tactile, olfactory)
- Potential mystery angles
- Names and relationships to verify

TARGET: 8-12 chunks of usable research.' | python ~/.claude/scripts/qdrant-store-gemini.py --collection "tesla_mandela_effects" --session "ep{{EPISODE_NUM}}-research"

Report:
- Existing lore relevant to this episode
- New research stored
- Potential contradictions to avoid
```

---

## Phase 1: Generate

**Spawn a Haiku supervisor to generate the full episode via Gemini.**

See `prompts/generation.md` for the complete generation template with all 14 editorial priorities.

---

## Phase 2: Editorial Pipeline (16 Agents)

**Run agents 01-16 sequentially on the draft.**

### Quick Start

```
# For each agent 01-16:
1. Read agent file: prompts/editorial/agents/[NN]-[name].md
2. Load current draft
3. Execute agent's ONE job
4. Save output as input for next agent
```

### Full Documentation

See `prompts/editorial/agents/ORCHESTRATION.md` for:
- Complete pipeline instructions
- Partial pipeline options
- Agent communication (03 → 16 handoff)
- Quality checkpoints
- Troubleshooting

---

## Phase 3: Validate

Run through app analyzers:
```bash
# If app validation available:
cd ~/projects/WARDENCLYFFE && npm run analyze:episode /path/to/episode.txt
```

Or manual review with the 16-agent checklist from ORCHESTRATION.md.

---

## Phase 4: Archive to Qdrant

Store episode facts to `episode_canon` collection:

```bash
~/.claude/scripts/gemini-account.sh 1 'Extract facts from this episode for the series canon.

EPISODE: {{EPISODE_NUM}} - {{TITLE}}

[Episode text here]

Return JSON:
{
  "characters": [
    {"name": "...", "fact_type": "appearance|action|dialogue|relationship", "fact": "...", "scene": "..."}
  ],
  "events": [
    {"event": "...", "timestamp": "...", "significance": "..."}
  ],
  "relationships": [
    {"character1": "...", "character2": "...", "relationship": "..."}
  ],
  "physical_descriptions": [
    {"subject": "...", "description": "...", "scene": "..."}
  ]
}' | python ~/.claude/scripts/qdrant-store-gemini.py --collection "episode_canon" --session "ep{{EPISODE_NUM}}-canon"
```

---

## The Gold Standard: Episode 2

**Episode 2 is the craft template.** Not Episode 1.

Episode 1 sets up the series premise. Episode 2 is where the artistic, audio-rich imagery was painstakingly created:

- Sensory expansion patterns (same concept, different body locations, different modalities)
- Writing that lands in the listener's body
- Audio-first: no reader, no turning back, only forward

**Example from Episode 2 (Electrical Damage Concept):**

First instance (hand, temperature):
> "The spark... arced from the metal to the meat of his hand and held there, searing a perfect circle into his skin."

Second instance (forearm/teeth/wrist, kinetic):
> "His arm locked. The current seized the muscles in his forearm and clamped his fingers around the key. He couldn't let go. His teeth rattled. The bones in his wrist vibrated like a struck tuning fork."

Third instance (thumb, pressure/occupation):
> "His thumb throbbed—not with the fading ache of a burn, but with the persistent pressure of occupation. As if the spark hadn't just damaged the skin. As if it had moved in."

**Notice:** Same concept. Zero repeated words. Each instance is a complete mini-narrative.

---

## Sensory Inventory

### Body Location Cycle (8 regions)

| Region | Specific Parts |
|--------|---------------|
| HEAD | temples, occipital ridge, jaw, larynx, behind the eyes |
| CHEST | sternum, ribs, intercostal muscles, diaphragm, pleura |
| BACK | scapulae, trapezius, lumbar, vertebrae, spinal column |
| ARMS | forearm, bicep, wrist, ulna, metacarpals |
| HANDS | palm, fingertips, knuckles, thenar, phalanges |
| CORE | solar plexus, vagus nerve, abdominal wall, pelvis |
| LEGS | quadriceps, hamstring, knee, ankle, metatarsals |
| SKIN | surface, subcutaneous, dermis, follicles |

### Sensory Modality Cycle (6 modalities)

| Modality | Variations |
|----------|------------|
| TEMPERATURE | cold, heat, absence of temperature, thermal gradient |
| PRESSURE | weight, occupation, compression, absence of pressure |
| TEXTURE | smooth, rough, grain, absence of texture, numbness |
| MOVEMENT | vibration, pulse, stillness, oscillation, tremor |
| PAIN | sharp, dull, burning, absence of pain, phantom |
| PROPRIOCEPTION | balance, position, drift, groundedness, vertigo |

### Micro-Narrative Templates

- **Negation chain:** "Not X. Not Y. This was Z."
- **Agency inversion:** The sensation acts; the character receives
- **Domestic metaphor:** tenant, home, room, architecture, occupation

---

## Quick Reference

| Phase | Who | Tool |
|-------|-----|------|
| Research | Haiku → Gemini | Task + gemini-account.sh |
| Generate | Haiku → Gemini | Task + gemini-account.sh |
| Edit (16 agents) | Claude (this session) | Read, Edit |
| Validate | App or Manual | Bash or Checklist |
| Archive | Haiku → Gemini | Task + qdrant-store-gemini.py |

---

## File Structure

```
~/.claude/skills/wardenclyffe-episode-writer/
├── SKILL.md                    (this file)
├── MEMORY.md
├── examples/
│   └── ep2-gold-standard.md
├── prompts/
│   ├── generation.md
│   └── editorial/
│       ├── [ARCHIVED] sweep-1-structure-opening.md
│       ├── [ARCHIVED] sweep-2-voice-perspective.md
│       ├── [ARCHIVED] sweep-3-term-frequency-sensory.md
│       ├── [ARCHIVED] sweep-4-clarity-polish.md
│       ├── [ARCHIVED] sweep-5-accuracy.md
│       └── agents/                     (NEW - 16 AGENTS)
│           ├── 01-deduplicator.md
│           ├── 02-anchor.md
│           ├── 03-term-counter.md
│           ├── 04-you-density.md
│           ├── 05-opening-hook.md
│           ├── 06-transitions.md
│           ├── 07-payoff-tracker.md
│           ├── 08-bridge-balancer.md
│           ├── 09-narrator-eraser.md
│           ├── 10-jargon-killer.md
│           ├── 11-dread-enforcer.md
│           ├── 12-relation-verifier.md
│           ├── 13-fact-checker.md
│           ├── 14-name-economist.md
│           ├── 15-clone-detector.md
│           ├── 16-sensory-expander.md
│           └── ORCHESTRATION.md
```

---

## Archived: Old 5-Sweep System

The original sweep files are preserved in `prompts/editorial/` but should not be used. They bundled multiple priorities together, causing the whack-a-mole problem where fixing one rule broke another.

Use the 16-agent pipeline instead.

---

*This skill was built because the in-app Episode Forge kept failing. AI thinks in labels. Humans write in sensations. Episode 2 shows how to bridge that gap. The 16-agent refactoring ensures each priority is enforced without interference.*
