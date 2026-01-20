# Episode Generation Prompt for Gemini

Use this prompt with `gemini-account.sh` to generate a complete episode draft.

---

## Variables to Replace

| Variable | Description |
|----------|-------------|
| `{{EPISODE_NUM}}` | Episode number (e.g., 3) |
| `{{TITLE}}` | Episode title (e.g., "The Vanishing Point") |
| `{{HISTORICAL_PERIOD}}` | Era/event being covered (e.g., "Tunguska Event, 1908") |
| `{{OUTLINE}}` | Scene-by-scene outline with emotional beats |
| `{{CANON_CONTEXT}}` | Summary from Qdrant research (characters, established facts) |

---

## The Prompt

```
You are writing Episode {{EPISODE_NUM}} of Tesla Mandela Effects, an audio drama series.

## CRITICAL: THIS IS AUDIO-FIRST

Listeners cannot turn back the page. They cannot re-read a confusing sentence. Every sentence must land in their body. They only move forward.

## SERIES CONTEXT

{{CANON_CONTEXT}}

## EPISODE 2 IS THE GOLD STANDARD

Episode 2 ("The Lion vs The Wolf") is the craft template. Study these patterns:

### Opening Hook
"Have you ever heard a dead machine scream?"
- Direct question creates intimacy
- "Dead machine" is a paradox
- NO dates, locations, or context in first sentence
- Creates vertigo immediately

### Sensory Expansion (The Episode 2 Formula)
The same concept (electrical damage) expressed THREE times using different body locations and modalities:

INSTANCE 1 (Hand / Temperature):
"The spark that jumped was not the thin blue snap of static. This was white. Thick as a matchstick. It arced from the metal to the meat of his hand and held there, searing a perfect circle into his skin."

INSTANCE 2 (Forearm, Teeth, Wrist / Kinetic):
"His arm locked. The current seized the muscles in his forearm and clamped his fingers around the key. He couldn't let go. His teeth rattled. The bones in his wrist vibrated like a struck tuning fork."

INSTANCE 3 (Thumb / Pressure-Occupation):
"His thumb throbbed—not with the fading ache of a burn, but with the persistent pressure of occupation. As if the spark hadn't just damaged the skin. As if it had moved in."

Pattern: Same concept. Zero repeated words. Each instance is a complete mini-narrative.

### Micro-Narrative Templates
- Negation chain: "Not X. Not Y. This was Z."
- Agency inversion: The sensation acts; the character receives
- Domestic metaphor: tenant, home, room, architecture, occupation

### Breath Paragraphs (Location Changes)
"Four thousand miles away. The Caribbean Sea. The brigantine Southern Cross. Captain Whitmore was in his cabin. It was noon. The ship was becalmed. The sails were hanging limp."

Elements: Distance marker, location named, specific vessel, character introduced, sensory grounding.

## THE 14 EDITORIAL PRIORITIES

### TIER 1 - HARD ENFORCEMENT (Stop and fix if violated)

P11 OPENING HOOK: First sentence must create vertigo or wrongness. NO dates, locations, or context. The listener decides in seconds whether to stay.

P4 DESCRIPTION OVER TERMINOLOGY: Show what happens to the body. No medical jargon.
- BAD: "The graft versus host response initiated a cascade of cytotoxic T-cell activity"
- GOOD: "The body recognized the foreign tissue and attacked it—white cells swarming, inflammation spreading like fire"

P1 SPECULATIVE BRIDGE: 3:1 facts to questions. State history definitively. State interpretation speculatively.
- BAD: "The death was an erasure. The universe had identified him as wrong."
- GOOD: "The paper is warped. The ink sits heavy. The spacing varies. Had the priest's hand been shaking?"

P9 MAJOR TRANSITIONS: Every location/time jump needs a breath paragraph that resets the listener's mental stage.

### TIER 2 - STRONG GUIDANCE

P2 INVISIBLE NARRATOR: No "I", no "we" actions. Narrator has no identity, no journey.
- BAD: "We discovered a letter in the archive"
- GOOD: "A letter surfaced in the archive"

P10 PRONOUN CLARITY: Re-anchor names every 2-3 sentences. Listeners lose track of "she/he" quickly.

P6 HISTORIAN TRAP: Research should unsettle, not prove. The goal is dread, not education.
- BAD: "Dr. Miroslav Petrovic, whose 1987 paper in Journal of Serbian Historical Studies (Vol. 42, Issue 3)..."
- GOOD: "A researcher spent four years analyzing records. What he found cost him his academic career."

### TIER 3 - AWARENESS (Claude will fix in editing sweeps)

P5 TERM FREQUENCY: 5-use cap per body-related term category. Track these:
- INFECTION: infection, contamination, colonization, infiltration
- FEVER: fever, heat, burning, temperature, warmth
- TISSUE: tissue, flesh, cells, material, substance
- HOLLOW: hollow, void, emptiness, absence, cavity
- BODY: body, organism, host, system, vessel
- WOUND: wound, damage, injury, cut, tear

P3 NAME ECONOMY: Maximum 6 unusual names per episode. One-time characters get descriptions, not names.

P14 "YOU" DENSITY: Save "you" for the ending. Maximum 8 before the Metastasis section. 80% should appear in the final Prognosis.

P12 SETUP/PAYOFF: Everything introduced must pay off or be marked as open thread.

P13 CLONING PREVENTION: Create unique sensory palette for this episode. Do not recycle Episode 1 imagery (grinding, 1-2-3 pulse, copper/ozone smell).

P7 RELATIONAL ACCURACY: Get relationships right (nephew, not cousin) or remove names.

P8 MICRO-FACT VERIFICATION: Every detail must be accurate. Calculate ages from birth/event years.

## SENSORY INVENTORY

### Body Location Cycle (Use variety)
- HEAD: temples, occipital ridge, jaw, larynx, behind the eyes
- CHEST: sternum, ribs, intercostal muscles, diaphragm
- BACK: scapulae, trapezius, lumbar, vertebrae
- ARMS: forearm, bicep, wrist, ulna
- HANDS: palm, fingertips, knuckles, thenar
- CORE: solar plexus, vagus nerve, abdominal wall
- LEGS: quadriceps, hamstring, knee, ankle
- SKIN: surface, subcutaneous, dermis, follicles

### Sensory Modality Cycle (Use variety)
- TEMPERATURE: cold, heat, absence of temperature
- PRESSURE: weight, occupation, compression
- TEXTURE: smooth, rough, grain, numbness
- MOVEMENT: vibration, pulse, stillness, tremor
- PAIN: sharp, dull, burning, phantom
- PROPRIOCEPTION: balance, position, drift, vertigo

## OUTLINE

{{OUTLINE}}

## INSTRUCTIONS

1. Open with P11-compliant hook (vertigo/wrongness, no dates/locations)
2. Use breath paragraphs at every major transition (P9)
3. Track body-related terms - aim for 5 uses max each (P5)
4. Replace any term you want to repeat with a sensory micro-story (P4)
5. State facts definitively, interpretation as questions (P1)
6. Save "you" for the Prognosis ending (P14)
7. Create UNIQUE sensory palette for this episode (P13)

Target: 8,500-16,000 words (minimum 8,500).
Write the complete episode.

Return ONLY the episode text, no commentary.
```

---

## How to Use

### Via Haiku Supervisor

```
Task tool:
  subagent_type: "general-purpose"
  model: "haiku"
  prompt: |
    Generate Episode {{EPISODE_NUM}}: "{{TITLE}}" via Gemini.

    ~/.claude/scripts/gemini-account.sh 1 '[FULL PROMPT ABOVE]' > /tmp/ep{{EPISODE_NUM}}_draft.txt

    Report word count and confirm draft saved.
```

### Direct (for testing)

```bash
~/.claude/scripts/gemini-account.sh 1 '[FULL PROMPT]' > /tmp/episode_draft.txt
wc -w /tmp/episode_draft.txt
```

---

## After Generation

Read the draft and perform the 5 editing sweeps (see `prompts/editorial/sweep-*.md`).
