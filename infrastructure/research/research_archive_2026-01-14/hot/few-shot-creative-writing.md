---
topic: "few-shot-creative-writing"
category: "gemini"
tier: "hot"
tags:
  - "llm-writing"
  - "few-shot-learning"
  - "example-injection"
  - "style-mimicry"
  - "episode-forge"
  - "llm-writing"
  - "few-shot-learning"
  - "example-injection"
  - "style-mimicry"
  - "episode-forge"
created: "2026-01-13 04:35 AM"
last_accessed: "2026-01-13 04:57 AM"
access_count: 2
---

## 2026-01-13 04:57 AM | Session: ResearchFix

Loaded cached credentials.
Here is a guide on how to use few-shot examples effectively for creative writing generation, based on current best practices.

### 1. Optimal Number of Examples

The consensus for creative writing is that **3 to 5 examples** provide the best results.

*   **1 Example:** Often leads to the model either matching the *topic* too closely or misinterpreting the stylistic instruction.
*   **3-5 Examples:** This range is the sweet spot. It's enough to establish a clear pattern of the desired style, tone, and structure without confusing the model or consuming too many tokens.
*   **5+ Examples:** The benefits diminish rapidly. Too many examples can introduce noise, increase the risk of the model latching onto irrelevant details, and may not significantly improve the quality of the output.

### 2. Example Length

The ideal length for an example is a **well-developed paragraph**.

*   **Too Short (a single sentence):** Insufficient for the model to grasp complex stylistic nuances like pacing, sentence variation, and narrative voice.
*   **Too Long (multiple pages):** Inefficient and can cause the model to lose focus on the core instructions.
*   **Just Right (a solid paragraph):** This provides enough text to showcase sentence structure, vocabulary, tone, and rhythm, giving the model a concrete sample to learn from.

### 3. How to Frame Examples in Prompts

The most effective method is to place **instructions first, followed by clearly labeled examples**. This primes the model with the goal and then provides the evidence.

*   **Placement:** Always put your core instructions at the top. The examples should follow, and the final prompt for the model to complete should come at the very end.
*   **Labeling:** Use clear, consistent labels for your examples. Simple labels like `[Good Example]` and `[Bad Example]` or more descriptive XML-style tags like `<style_to_emulate>` and `</style_to_avoid>` work very well.

### 4. Use of "Good" and "Bad" Contrastive Examples

**Yes, using contrastive examples is highly effective.** It sharpens the model's understanding by showing it not only what to do, but what *not* to do. This is particularly useful for refining tone and avoiding common creative writing pitfalls.

By providing a "bad" example, you give the model a clear negative target to avoid, which helps it better understand the boundaries of the desired style.

### 5. Preventing Verbatim Copying

This is a critical step. To preserve style without plagiarism, you must be explicit in your instructions.

1.  **Deconstruct the Style:** In your instructions, break down *why* the "good" examples are good. Don't just show, *tell*. For example: "Notice the use of short, punchy sentences mixed with longer, descriptive ones. The tone is cynical but humorous."
2.  **Add a Negative Constraint:** Explicitly forbid copying. A simple instruction like, "Generate a new piece in this style, but do not use any of the same sentences or specific phrasings from the examples," is very effective.
3.  **Focus on "Principles":** Frame the task as learning the *principles* of the style, not the content.

### 6. Specific Prompt Templates

Here are two practical prompt templates that put all these principles together.

---

#### Template 1: Emulating a Specific Author's Style

**Goal:** Write a new passage in the style of Raymond Chandler.

```
Your task is to write a short, original piece of descriptive narrative in the hardboiled detective style of Raymond Chandler.

Your writing should capture the following stylistic elements:
- A cynical, world-weary, and witty first-person narrator.
- The use of evocative, original similes and metaphors (e.g., "The air was thick enough to paddle in.").
- Short, observational sentences mixed with longer, more introspective ones.
- A detached, observational tone that still conveys a strong sense of mood and place.

---
Here are examples of the style to emulate.

<style_to_emulate>
The lobby was high and cool and smelled of expensive leather and stale cigar smoke. A hush had come over the room, the kind of hush that usually means somebody with a lot of money has just walked in. He was a tall man, with a face that had been handsome once and was now just interesting. He moved with the slow, deliberate grace of a man who has never had to hurry.
</style_to_emulate>

<style_to_emulate>
She gave me a smile I could feel in my hip pocket. It was the kind of smile that could send a bishop through a stained-glass window. Her voice was low and husky, a voice that had been dragged over gravel and dipped in honey. "I've been expecting you," she said, and I knew right then that my day had just taken a turn for the complicated.
</style_to_emulate>

---
Now, here is an example of the style to AVOID. It is too generic and lacks a distinctive voice.

<style_to_avoid>
The hotel lobby was very nice. A man walked in who seemed important. He was tall and looked like he used to be handsome. He walked slowly. A woman smiled at me. Her voice was deep. She said she was waiting for me.
</style_to_avoid>

---
IMPORTANT INSTRUCTION: Do not use any of the specific phrases, sentences, or character descriptions from the examples above. Your work must be entirely original.

Now, write a short paragraph describing a dusty, forgotten bookstore, in the style of Raymond Chandler.
```

---

#### Template 2: Establishing a Specific Tone (Sci-Fi Horror)

**Goal:** Write a log entry with a tone of growing dread and paranoia.

```
Your task is to write a new, original captain's log entry for a sci-fi horror story.

The style should be:
- First-person perspective.
- The tone should be one of mounting dread, paranoia, and psychological distress.
- The prose should be concise and professional at the start, but gradually become more fragmented and emotional.
- The sentences should become shorter and more disjointed as the entry progresses.

---
Here are examples of the style to emulate.

<style_to_emulate>
Captain's Log, Stardate 4513.4. We've been holding orbit around Kepler-186f for three days now. All long-range scans show nothing but silence. The crew is on edge. Something about this place feels... wrong. The silence is too deep. It's like the universe is holding its breath.
</style_to_emulate>

<style_to_emulate>
Log Entry, Supplemental. The comms are still dead. I swear I hear whispers in the static, echoes of voices that aren't there. Jenkins saw something outside the viewport yesterday. A shadow. Just a flicker. But he hasn't slept since. None of us have. The silence is screaming now.
</style_to_emulate>

---
Here is an example of the style to AVOID. The tone is too action-oriented and not psychological.

<style_to_avoid>
Captain's Log. We are in orbit. The planet is quiet. The crew is nervous. Suddenly, an alien ship appeared and started firing at us! We fired back with our phasers.
</style_to_avoid>

---
IMPORTANT INSTRUCTION: Your log entry must be completely original and not use any of the specific events or phrases from the examples provided.

Now, write a new captain's log entry about the ship's botanist, Dr. Aris, who has been spending too much time alone in the ship's arboretum after bringing back a new plant specimen.
Here is a comprehensive guide to using few-shot examples for creative writing generation, addressing your research questions with practical advice and templates.

### 1. Optimal Number of Examples

The consensus from research and best practices suggests that the optimal number of examples for creative writing is **3 to 5**.

*   **1 Example:** Often too few. The model may overfit to the specific content of the single example rather than abstracting the style. It can lead to more direct copying or misunderstanding the stylistic nuances.
*   **3 Examples:** This is the sweet spot for many creative tasks. It's enough to establish a clear pattern of tone, sentence structure, and voice without overwhelming the model.
*   **5 Examples:** Use for more complex or nuanced styles. If the style has multiple facets (e.g., shifts in tone, complex character voices), 5 examples can provide the necessary depth for the model to learn from.
*   **More than 5:** This generally leads to diminishing returns. The context window gets filled, and the model may get "confused" by too much information, or the cost (in tokens) increases for no significant benefit.

**Recommendation:** Start with **3** high-quality examples. If the output isn't quite right, increase to 5.

### 2. What Length of Examples Works Best?

**Concise and focused examples are more effective than long, rambling ones.** The goal is to provide a "distilled" version of the style you want to emulate.

*   **Paragraph-Length:** For prose, providing 1-3 paragraph examples is ideal. This is long enough to demonstrate sentence flow, paragraph structure, and voice, but short enough to be easily processed.
*   **Stanza-Length:** For poetry, a single stanza per example is often sufficient to show rhythm, rhyme scheme, and metaphorical language.
*   **Dialogue Snippets:** For screenwriting or fiction with heavy dialogue, provide short back-and-forth exchanges (2-4 lines per character) to demonstrate pacing and subtext.

**Key Principle:** Each example should be a potent demonstration of the target style. Don't dilute it with unnecessary plot or exposition.

### 3. How to Frame Examples in Prompts

Placement and labeling are critical for guiding the model effectively. The best practice is to provide clear instructions *first*, then the examples, and finally, the prompt for the new creation. Use clear, consistent labels.

**Structure:**

1.  **Role and Goal:** Start by telling the model what it is (e.g., "You are a creative writing assistant specializing in literary fiction.").
2.  **Instructions:** Clearly state the task, the stylistic goals, and any constraints.
3.  **Examples:** Provide your examples with clear labels.
4.  **Prompt:** The final instruction for what to write.

**Placement:** Always place the examples *before* the final prompt for the new text. Models give more weight to the information that comes just before the final instruction.

### 4. "Good" vs. "Bad" Contrastive Examples

Using contrastive examples is a powerful technique to refine the model's understanding. By showing the model what *not* to do, you create clearer boundaries for the desired style.

**When to Use:**
*   When the desired style is subtle and could be easily misinterpreted.
*   When you want to avoid specific clichés, tones, or phrasings.
*   When initial attempts with only "good" examples are not producing the desired results.

**Recommendation:** Use them sparingly but strategically. One or two "bad" examples are usually enough to make the point.

### 5. Preventing Verbatim Copying and Preserving Style

This is the most challenging aspect. The key is to force the model to generalize the *rules* of the style, not the *content*.

**Techniques:**

1.  **Explicit Prohibition:** In your instructions, state clearly: *"Do not use the same characters, settings, or specific plot points from the examples. Your task is to capture the style, not the content. Avoid using exact phrases or sentences from the examples."*
2.  **Analyze the Style for the Model:** Deconstruct the style in your instructions. For example: *"Notice how the examples use short, punchy sentences followed by longer, more descriptive ones. The tone is detached and observational. Use this pattern in your writing."*
3.  **Diverse Examples:** Use examples that are different in subject matter but consistent in style. This teaches the model that the style is transferable.
4.  **Higher "Temperature":** If you can control the model's parameters, a higher temperature (e.g., 0.8-1.0) encourages more randomness and creativity, making verbatim copying less likely.

### 6. Specific Prompt Templates

Here are three practical templates for different creative writing tasks.

---

#### Template 1: Emulating a Prose Style (e.g., Raymond Carver)

```
You are a creative writing assistant. Your goal is to write a short piece of fiction in a minimalist, "dirty realism" style, similar to Raymond Carver.

**Instructions:**
*   Write a short story opening (1-2 paragraphs).
*   The tone should be detached, melancholic, and observational.
*   Use simple, direct language.
*   Focus on external actions and dialogue, hinting at internal turmoil without stating it directly.
*   Do not use any of the specific characters, settings, or plot points from the examples.

**Style Examples:**

<example>
The man and the woman sat at the kitchen table. The light from the window was gray. He pushed a salt shaker back and forth. She watched his hand. "I'm leaving," he said, not looking at her. She nodded, as if he'd just commented on the weather.
</example>

<example>
He poured another drink. The ice cracked in the glass. Outside, a dog was barking. It was a lonely sound. He thought about calling his ex-wife, but he knew she wouldn't answer. He drank. The whiskey burned.
</example>

<example>
She stood at the bus stop, her coat pulled tight. The wind was cold. A car drove by, its headlights cutting through the dusk. She didn't know where she was going, only that she had to go somewhere.
</example>

**Your Task:**
Write a new story opening, in the same style, about a man who has just lost his job.
```

---

#### Template 2: Contrastive Examples for Tone (e.g., Humorous Sci-Fi)

```
You are a sci-fi writer with a knack for humor, in the vein of Douglas Adams.

**Instructions:**
*   Write a short scene (2-3 paragraphs) about a spaceship's computer delivering bad news.
*   The style should be witty, satirical, and filled with cosmic irony.
*   The computer should be overly cheerful and bureaucratic.

**Good Style Example:**

<good_example>
The ship's computer, a cheerful entity named "Marvin's More Upbeat Cousin," chimed pleasantly. "Good morning, Captain! I have wonderful news. We have successfully identified the source of the strange noise. The bad news is that it's a micro-singularity, and it is currently consuming the port engine. On the bright side, the view is spectacular!"
</good_example>

**Bad Style Example (What to Avoid):**

<bad_example>
"Captain, the port engine is malfunctioning," the computer said in a monotone voice. "There is a singularity in close proximity. We are in danger."
</bad_example>

**Your Task:**
Write a new scene, in the **good** style, where the ship's computer announces that the life support system has been replaced with a trial version of a new soft drink dispenser.
```

---

#### Template 3: Poetry Style Transfer

```
You are a poet. Your task is to write a short poem in the style of Emily Dickinson.

**Instructions:**
*   Write a four-line poem about the feeling of loneliness.
*   Use slant rhymes and unconventional capitalization.
*   Employ dashes to create pauses and emphasize words.
*   The poem should be introspective and use a simple, yet profound, central metaphor.
*   Do not copy the specific metaphors or phrasing from the examples.

**Style Examples:**

<example>
The Soul has Bandaged moments –
When too appalled to stir –
She feels some ghastly Fright come up
And stop to look at her –
</example>

<example>
There is a solitude of space
A solitude of sea
A solitude of death, but these
Society shall be
</example>

<example>
A great Hope fell
You heard no noise
The Ruin was within
Oh cunning wreck that told no tale
And let no Witness in
</example>

**Your Task:**
Write a new, four-line poem in the same style, using the metaphor of an empty room to describe loneliness.
```
Here is a comprehensive guide to using few-shot examples effectively for creative writing generation, addressing your research questions with practical advice and templates.

### 1. Optimal Number of Examples

The consensus from research and best practices suggests that the optimal number of examples for creative writing is **3 to 5**.

*   **1 Example:** Often too few. The model may overfit to the specific content of the single example rather than abstracting the style. It can lead to more direct copying or misunderstanding the stylistic nuances.
*   **3 Examples:** This is the sweet spot for many creative tasks. It's enough to establish a clear pattern of tone, sentence structure, and voice without overwhelming the model.
*   **5 Examples:** Use for more complex or nuanced styles. If the style has multiple facets (e.g., shifts in tone, complex character voices), 5 examples can provide the necessary depth for the model to learn from.
*   **More than 5:** This generally leads to diminishing returns. The context window gets filled, and the model may get "confused" by too much information, or the cost (in tokens) increases for no significant benefit.

**Recommendation:** Start with **3** high-quality examples. If the output isn't quite right, increase to 5.

### 2. What Length of Examples Works Best?

**Concise and focused examples are more effective than long, rambling ones.** The goal is to provide a "distilled" version of the style you want to emulate.

*   **Paragraph-Length:** For prose, providing 1-3 paragraph examples is ideal. This is long enough to demonstrate sentence flow, paragraph structure, and voice, but short enough to be easily processed.
*   **Stanza-Length:** For poetry, a single stanza per example is often sufficient to show rhythm, rhyme scheme, and metaphorical language.
*   **Dialogue Snippets:** For screenwriting or fiction with heavy dialogue, provide short back-and-forth exchanges (2-4 lines per character) to demonstrate pacing and subtext.

**Key Principle:** Each example should be a potent demonstration of the target style. Don't dilute it with unnecessary plot or exposition.

### 3. How to Frame Examples in Prompts

Placement and labeling are critical for guiding the model effectively. The best practice is to provide clear instructions *first*, then the examples, and finally, the prompt for the new creation. Use clear, consistent labels.

**Structure:**

1.  **Role and Goal:** Start by telling the model what it is (e.g., "You are a creative writing assistant specializing in literary fiction.").
2.  **Instructions:** Clearly state the task, the stylistic goals, and any constraints.
3.  **Examples:** Provide your examples with clear labels.
4.  **Prompt:** The final instruction for what to write.

**Placement:** Always place the examples *before* the final prompt for the new text. Models give more weight to the information that comes just before the final instruction.

### 4. "Good" vs. "Bad" Contrastive Examples

Using contrastive examples is a powerful technique to refine the model's understanding. By showing the model what *not* to do, you create clearer boundaries for the desired style.

**When to Use:**
*   When the desired style is subtle and could be easily misinterpreted.
*   When you want to avoid specific clichés, tones, or phrasings.
*   When initial attempts with only "good" examples are not producing the desired results.

**Recommendation:** Use them sparingly but strategically. One or two "bad" examples are usually enough to make the point.

### 5. Preventing Verbatim Copying and Preserving Style

This is the most challenging aspect. The key is to force the model to generalize the *rules* of the style, not the *content*.

**Techniques:**

1.  **Explicit Prohibition:** In your instructions, state clearly: *"Do not use the same characters, settings, or specific plot points from the examples. Your task is to capture the style, not the content. Avoid using exact phrases or sentences from the examples."*
2.  **Analyze the Style for the Model:** Deconstruct the style in your instructions. For example: *"Notice how the examples use short, punchy sentences followed by longer, more descriptive ones. The tone is detached and observational. Use this pattern in your writing."*
3.  **Diverse Examples:** Use examples that are different in subject matter but consistent in style. This teaches the model that the style is transferable.
4.  **Higher "Temperature":** If you can control the model's parameters, a higher temperature (e.g., 0.8-1.0) encourages more randomness and creativity, making verbatim copying less likely.

### 6. Specific Prompt Templates

Here are three practical templates for different creative writing tasks.

---

#### Template 1: Emulating a Prose Style (e.g., Raymond Carver)

```
You are a creative writing assistant. Your goal is to write a short piece of fiction in a minimalist, "dirty realism" style, similar to Raymond Carver.

**Instructions:**
*   Write a short story opening (1-2 paragraphs).
*   The tone should be detached, melancholic, and observational.
*   Use simple, direct language.
*   Focus on external actions and dialogue, hinting at internal turmoil without stating it directly.
*   Do not use any of the specific characters, settings, or plot points from the examples.

**Style Examples:**

<example>
The man and the woman sat at the kitchen table. The light from the window was gray. He pushed a salt shaker back and forth. She watched his hand. "I'm leaving," he said, not looking at her. She nodded, as if he'd just commented on the weather.
</example>

<example>
He poured another drink. The ice cracked in the glass. Outside, a dog was barking. It was a lonely sound. He thought about calling his ex-wife, but he knew she wouldn't answer. He drank. The whiskey burned.
</example>

<example>
She stood at the bus stop, her coat pulled tight. The wind was cold. A car drove by, its headlights cutting through the dusk. She didn't know where she was going, only that she had to go somewhere.
</example>

**Your Task:**
Write a new story opening, in the same style, about a man who has just lost his job.
```

---

#### Template 2: Contrastive Examples for Tone (e.g., Humorous Sci-Fi)

```
You are a sci-fi writer with a knack for humor, in the vein of Douglas Adams.

**Instructions:**
*   Write a short scene (2-3 paragraphs) about a spaceship's computer delivering bad news.
*   The style should be witty, satirical, and filled with cosmic irony.
*   The computer should be overly cheerful and bureaucratic.

**Good Style Example:**

<good_example>
The ship's computer, a cheerful entity named "Marvin's More Upbeat Cousin," chimed pleasantly. "Good morning, Captain! I have wonderful news. We have successfully identified the source of the strange noise. The bad news is that it's a micro-singularity, and it is currently consuming the port engine. On the bright side, the view is spectacular!"
</good_example>

**Bad Style Example (What to Avoid):**

<bad_example>
"Captain, the port engine is malfunctioning," the computer said in a monotone voice. "There is a singularity in close proximity. We are in danger."
</bad_example>

**Your Task:**
Write a new scene, in the **good** style, where the ship's computer announces that the life support system has been replaced with a trial version of a new soft drink dispenser.
```

---

#### Template 3: Poetry Style Transfer

```
You are a poet. Your task is to write a short poem in the style of Emily Dickinson.

**Instructions:**
*   Write a four-line poem about the feeling of loneliness.
*   Use slant rhymes and unconventional capitalization.
*   Employ dashes to create pauses and emphasize words.
*   The poem should be introspective and use a simple, yet profound, central metaphor.
*   Do not copy the specific metaphors or phrasing from the examples.

**Style Examples:**

<example>
The Soul has Bandaged moments –
When too appalled to stir –
She feels some ghastly Fright come up
And stop to look at her –
</example>

<example>
There is a solitude of space
A solitude of sea
A solitude of death, but these
Society shall be
</example>

<example>
A great Hope fell
You heard no noise
The Ruin was within
Oh cunning wreck that told no tale
And let no Witness in
</example>

**Your Task:**
Write a new, four-line poem in the same style, using the metaphor of an empty room to describe loneliness.
```

---


## 2026-01-13 04:35 AM | Session: ResearchAgent


