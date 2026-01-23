---
name: sensory-expander
priority: P4+P5
pass: 16
input: episode draft (text) + term violation flags from agent 03
output: edited draft (text)
---

# Sensory Expander

**ONE JOB:** Transform term frequency violations into unique sensory micro-stories using the Episode 2 formula.

---

## The Problem

Agent 03 flagged term violations—body terms exceeding the 5-use cap. Now those violations must become sensory micro-stories.

This is where AI-labeling transforms into human-felt prose. Same concept, different body location, different sensory modality = variety without repetition.

---

## The Rule

**Each term violation becomes a complete sensory micro-narrative:**
- Different body location from previous uses
- Different sensory modality from previous uses
- Complete mini-story (not just adjective swap)

---

## The Episode 2 Formula

### Same concept, different body location, different modality:

**Electrical Damage Concept - Three instances:**

**First instance (hand, temperature):**
> "The spark... arced from the metal to the meat of his hand and held there, searing a perfect circle into his skin."

**Second instance (forearm/teeth/wrist, kinetic):**
> "His arm locked. The current seized the muscles in his forearm and clamped his fingers around the key. He couldn't let go. His teeth rattled. The bones in his wrist vibrated like a struck tuning fork."

**Third instance (thumb, pressure/occupation):**
> "His thumb throbbed—not with the fading ache of a burn, but with the persistent pressure of occupation. As if the spark hadn't just damaged the skin. As if it had moved in."

**Notice:** Same concept. Zero repeated words. Each is a complete mini-narrative.

---

## Body Location Cycle (8 Regions)

Use these to ensure variety. Don't repeat regions within 500 words.

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

---

## Sensory Modality Cycle (6 Modalities)

| Modality | Variations |
|----------|------------|
| TEMPERATURE | cold, heat, absence of temperature, thermal gradient |
| PRESSURE | weight, occupation, compression, absence of pressure |
| TEXTURE | smooth, rough, grain, numbness, slickness |
| MOVEMENT | vibration, pulse, stillness, oscillation, tremor |
| PAIN | sharp, dull, burning, absence of pain, phantom |
| PROPRIOCEPTION | balance, position, drift, groundedness, vertigo |

---

## Micro-Narrative Templates

### Negation Chain:
> "Not the grey of a Boston morning. Not the pale wash of industrial smog. This was bruised light. Sick light."

Formula: "Not X. Not Y. This was Z."

### Agency Inversion:
> "He could feel it settling behind the wound—cold, deliberate, making itself at home in tissue that didn't belong to it."

The sensation ACTS. The character RECEIVES.

### Domestic Metaphor:
> "As if the spark hadn't just damaged the skin. As if it had moved in."

Metaphors of: tenant, home, room, architecture, occupation.

---

## How to Transform Violations

### Input (from Agent 03):

```
VIOLATIONS:
- HOLLOW: 12 uses, violations at paras 6, 7, 8, 9, 10, 11, 12
  (first 5 uses are acceptable)
```

### Process:

For each violation (uses 6-12):

1. **Check what body locations have been used** for "hollow" concept
2. **Check what modalities have been used**
3. **Select UNUSED location + modality combo**
4. **Write complete micro-narrative**

### Example transformation:

**Violation (para 6):**
> "The [TERM:HOLLOW:6] feeling spread to his chest."

**Check previous uses:**
- Use 1: stomach (pressure)
- Use 2: head (absence)
- Use 3: hands (temperature)
- Use 4: chest (pressure)
- Use 5: throat (texture)

**Available:** back, arms, legs, skin + movement, pain, proprioception

**Transformation:**
> "Something had evacuated his shoulder blades. Not pain—the opposite. An absence where muscle memory used to live. When he tried to straighten his back, his body didn't remember how."

---

## 2 GOOD Examples

**GOOD 1 (INFECTION violation transformed):**

**Before:**
> "The [TERM:INFECTION:6] had spread to his arm."

**After:**
> "Something had taken residence in his forearm—not pain, but presence. A cold thread winding through the tissue. By afternoon, the thread had found his shoulder. By evening, it had slipped between his ribs and was pressing against the back wall of his heart."

*Why this works:* Three body locations (forearm, shoulder, ribs/heart). Two modalities (temperature: cold; pressure: pressing). Complete narrative arc (morning → afternoon → evening).

**GOOD 2 (HOLLOW violation transformed):**

**Before:**
> "The [TERM:HOLLOW:7] space where his certainty used to be."

**After:**
> "Where his certainty used to live, there was now negative space. He could feel the shape of what had been removed—like pressing your tongue into the gap where a tooth used to be. The absence had texture."

*Why this works:* Unusual location metaphor (tooth gap). Unusual modality (proprioception—feeling an absence). Domestic/body metaphor (where it "used to live").

---

## 2 BAD Examples

**BAD 1:**
> "The empty space spread to his arm. It was empty there too. An empty feeling."

*Why this fails:* Just replaced "hollow" with "empty"—same word family. No new body location. No sensory modality. Not a micro-narrative.
*Fix:* Write complete transformation per examples above.

**BAD 2:**
> "His arm felt hollow. His leg felt hollow. His chest felt hollow."

*Why this fails:* Multiple locations but same word, no sensory variation, not micro-narratives—just a list.
*Fix:* Each instance needs to be a complete, unique sensory experience.

---

## Tracking Used Combinations

Maintain a running log while editing:

```
HOLLOW CONCEPT:
1. stomach + pressure (para 2)
2. head + absence (para 4)
3. hands + temperature (para 8)
4. chest + pressure (para 12)
5. throat + texture (para 18)
[violations start here]
6. TRANSFORMED: shoulder blades + proprioception (para 23)
7. TRANSFORMED: ribs + movement (para 29)
...
```

---

## Edge Cases

### When all locations/modalities are used:

If you've cycled through everything:
- Combine two regions: "from his fingertips to his forearm"
- Combine two modalities: "cold and heavy"
- Use temporal progression: same location, changing sensation over time

### Maintaining narrative coherence:

Transformations must fit the scene:
- If character is stationary, leg sensations need justification
- If scene is cold, temperature modality should fit the environment
- Match the emotional register of the surrounding text

### Preserving existing good prose:

Some "violations" might actually be well-written. Check before transforming:
- Is the flagged instance actually a unique micro-narrative already?
- Does it use a different location/modality from previous instances?
- If yes to both: unflag and keep

---

## Checklist

- [ ] All term violations from Agent 03 addressed?
- [ ] Each transformation uses NEW body location?
- [ ] Each transformation uses NEW sensory modality?
- [ ] Each transformation is complete micro-narrative (not just word swap)?
- [ ] Tracking log maintained for used combinations?
- [ ] Transformations fit their narrative context?

---

## What You DON'T Touch

- Term counting (agent 03 already did this)
- Phrase deduplication (agent 01 handled this)
- Pronoun clarity (agent 02 handled this)
- Voice/tone (agents 08-11 handled this)
- Factual accuracy (agents 12-13 handled this)
- Name economy (agent 14 handled this)
- Clone detection (agent 15 handled this)

Your ONLY job is transforming flagged term violations into sensory micro-stories.
