---
topic: "llm-sensory-precision"
category: "gemini"
tier: "hot"
tags:
  - "llm-writing"
  - "sensory-precision"
  - "prompt-engineering"
  - "embodied-language"
  - "episode-forge"
  - "llm-writing"
  - "sensory-precision"
  - "embodied-language"
  - "episode-forge"
created: "2026-01-13 04:35 AM"
last_accessed: "2026-01-13 04:51 AM"
access_count: 2
---

## 2026-01-13 04:51 AM | Session: ResearchFix

Loaded cached credentials.
Of course. This is an excellent research question that gets to the heart of prompt engineering for creative and evocative text. Here is a detailed breakdown for improving LLM-generated sensory language in documentary scripts.

### 1. Why LLMs Default to Generic Sensory Words

LLMs generate statistically probable text based on their training data. Generic, abstract sensory language ("cold dread," "heart-pounding fear," "a wave of sadness") is far more common in the vast corpus of text they are trained on than precise, somatic descriptions. This creates a gravitational pull toward cliché for several reasons:

*   **High Statistical Frequency:** Phrases like "sinking feeling" are linguistic shortcuts that have appeared millions of times in books, articles, and scripts. For an LLM, this is a high-probability, "safe" response when asked to describe an emotion like anxiety.
*   **The Path of Least Resistance:** Describing "a hollow space behind the sternum" requires the synthesis of multiple, less-connected concepts: anatomy (`sternum`), spatial relationships (`behind`), and physical sensation (`hollow space`). This is a more complex and lower-probability word sequence than the tokenistically simpler "cold dread."
*   **Lack of Embodied Experience:** An LLM has never *felt* a sternum, a trapezius muscle, or a diaphragm seizing. Its understanding is a massive, multi-dimensional map of words and their relationships. It knows `fear` is linked to `heart` and `pounding`, but it doesn't have the first-person, physical memory that connects a specific stimulus to a specific, localized bodily sensation. We aren't asking it to remember a feeling; we are asking it to *construct a plausible description of one* based on text it has read.
*   **Authorial Abstraction:** In much of human writing, authors state the emotion first ("He felt a sudden dread") and *then* might follow up with physical details. The LLM often latches onto the initial, more common abstract statement and considers the task complete.

### 2. Specific Techniques to Force Body-Location Precision

To overcome the default, you must use prompts that constrain the LLM and force it out of its statistical comfort zone. The key is to shift the focus from naming the *emotion* to describing the *physical evidence* of the emotion.

**Technique 1: Direct Anatomical Targeting**
Explicitly name body parts in the prompt. This forces the LLM to anchor its description to a specific location.

*   **Bones:** "Describe the sensation that radiates from the **clavicle** and spreads through the **ribcage**."
*   **Muscles:** "Instead of 'his shoulders were tense,' describe the feeling in his **trapezius muscles** as if they were turning from flesh to stone."
*   **Nerve Centers/Plexuses:** The **solar plexus** and **vagus nerve** are excellent targets for describing anxiety, shock, and calm. "Describe the feeling of relief not as a thought, but as a signal activating the **vagus nerve**, slowing the heart and warming the chest."
*   **Specific Body Regions:** Use precise, evocative regions. Instead of "in his throat," try "in the **hollow of his throat**." Instead of "on his back," try "between his **scapulae**."

**Technique 2: The Metaphorical Bridge ("As If")**
This is the most powerful technique. You give the LLM a concrete physical metaphor to work with, which it can then translate into sensory language.

*   **Prompt:** "Describe the feeling in her stomach *as if* a handful of cold, smooth stones were being dropped into it one by one."
*   **Prompt:** "Describe the joy in his chest, not as a feeling, but *as if* a tightly coiled spring in his **diaphragm** finally released."
*   **Prompt:** "Write the sensation of dread in her limbs *as if* her blood were being replaced by slush."

**Technique 3: Focus on Verbs of Sensation**
Force the LLM to use strong, active verbs instead of adjectives. Frame the prompt around what the sensation is *doing*.

*   **Prompt:** "What does the anxiety *do* to the muscles around her eyes and jaw? Does it **cinch**, **pull**, **numb**, or **freeze** them? Describe that action."
*   **Prompt:** "Don't say he was 'nervous.' Describe how the energy **vibrates** in his hands. Is it a **hum**, a **thrum**, or a **prickling** sensation in his palms?"

**Technique 4: Role-Playing and Expert Persona**
Instruct the LLM to adopt the persona of someone who would naturally use precise language.

*   **Prompt:** "**You are a kinesiologist** writing a documentary script. Describe the physical posture of a subject experiencing deep grief. Focus on the curvature of the spine, the position of the scapulae, and the tension in the intercostal muscles."
*   **Prompt:** "**Adopt the persona of a classical singer.** Describe the feeling of stage fright, paying close attention to the diaphragm, the larynx, and the resonating cavities in the skull."

### 3. Example Transformations (Generic to Precise)

Here are examples applying the techniques.

**Example 1: "A gut-wrenching feeling"**
*   **Generic LLM Output:** `She got the news and felt a gut-wrenching feeling of despair.`
*   **Precision Prompt:** `Rewrite this. Focus the "gut-wrenching" feeling on the solar plexus and diaphragm. Use a metaphor of a physical action, like a sudden, upward motion.`
*   **Precise LLM Output:** `The words didn't register in her mind but in her solar plexus. Her diaphragm seized in a violent, upward scoop, forcing the air from her lungs in a silent gasp. It was a wrenching, hollow void where her breath and certainty used to be.`

**Example 2: "Her heart pounded with fear"**
*   **Generic LLM Output:** `Seeing the figure in the dark, her heart pounded with fear.`
*   **Precision Prompt:** `Go beyond the cliché 'heart pounded.' Describe the sensation from the inside. Is the rhythm regular or irregular? Describe how the pulse is felt in other parts of the body, specifically the hollow of the throat and the temples. Use the word "sternum."`
*   **Precise LLM Output:** `It wasn't just a pounding. It was a frantic, irregular slam against the inside of her ribs. She could feel each kick reverberating behind her sternum, while a secondary, hotter pulse began to beat in the hollow of her throat and at her temples.`

**Example 3: "A wave of relief"**
*   **Generic LLM Output:** `When the test came back negative, a wave of relief washed over him.`
*   **Precision Prompt:** `Transform "a wave of relief" into a specific physiological event. Start with the muscles in the shoulders and jaw. What do they do? Describe the sensation of breath changing in the lungs. Use the word "unclenching."`
*   **Precise LLM Output:** `The relief didn't wash over him; it started as a slow, deep unclenching in his jaw. The tension in his trapezius muscles, which he hadn't even noticed, suddenly dissolved, letting his shoulders drop. He finally drew a full breath, feeling it fill a space in his lungs that had felt tight and constricted for days.`

### 4. Anti-Patterns to Avoid

When prompting for precision, it's easy to fall into new traps.

*   **The Anatomy Chart:** Simply listing body parts is not evocative. `The sternocleidomastoid tensed and the trapezius tightened` is clinical, not creative. The anatomical term should be a scaffold for a *sensory* description, not the description itself.
*   **Vague Positive Instructions:** Prompts like "be more descriptive," "use sensory language," or "be more creative" are not specific enough. The LLM will likely just add more adjectives to its generic output (e.g., "a *deep, cold* dread"). You must provide concrete constraints and directions.
*   **Emotional Contamination:** Avoid starting the prompt with the name of the emotion. Instead of, `Describe the physical feeling of "shame,"` try prompting the cause and asking for the effect: `Describe the physical sensation of being caught in a lie. Focus on the skin on the face and neck. Does it feel hot, cold, tight, or prickly?` This forces the LLM to generate the physical evidence from which a reader infers shame.
*   **Overloading Metaphors:** One strong, clear metaphor is better than three weak ones. `Describe the feeling as if a block of ice were in his stomach, being hit by a hammer, while hornets buzzed in his ears` is confusing. Stick to a single, powerful "as if" statement per sensation.

---


## 2026-01-13 04:35 AM | Session: EpisodeForgeResearch


