---
topic: "llm-word-count-control"
category: "gemini"
tier: "hot"
tags:
  - "llm-writing"
  - "word-count"
  - "length-control"
  - "episode-forge"
  - "text-generation"
  - "llm-writing"
  - "word-count"
  - "length-control"
  - "episode-forge"
  - "iterative-expansion"
  - "prompt-engineering"
created: "2026-01-13 04:35 AM"
last_accessed: "2026-01-13 04:38 AM"
access_count: 2
---

## 2026-01-13 04:38 AM | Session: ResearchAgent

Loaded cached credentials.
Of course. This is a classic challenge with LLMs. They are optimized for information density and coherence, not verbosity. Simply asking for a word count is unreliable because it runs counter to their core training.

Achieving consistent word counts requires moving from a "single-shot generation" mindset to a "programmatic, multi-step orchestration" mindset. Here is a detailed guide based on practical, tested approaches.

### Executive Summary

The most reliable method is an **iterative expansion loop**. You generate a first draft, programmatically check its word count, and then repeatedly use the LLM to identify and flesh out specific sections with targeted prompts until you reach the desired length. This is far more effective than any single-prompt structure.

---

### 1. Prompt Structures to Prevent Compression

While not a complete solution, a strong initial prompt is crucial for getting a good first draft and minimizing the number of expansion iterations. The goal is to force the model to think in terms of structure and detail rather than just fulfilling a request.

**Ineffective (Common) Prompt:**
> "Continue the story. The next section is about the protagonist discovering the hidden library. It should be approximately 1200 words."

This fails because the model sees "1200 words" as a loose guideline, not a rigid constraint, and will prioritize finishing the "task" (describing the discovery) efficiently.

**Effective, De-compressing Prompt Structure:**
Use a combination of role-playing, explicit constraints, and a mandated structure. XML tags are particularly effective for helping models like Claude parse and adhere to complex instructions.

```xml
<system_prompt>
You are a verbose and descriptive narrative author. Your specialty is writing long-form, detailed episodic fiction. You never summarize. You expand on every detail, engage all five senses, and delve deep into character introspection. Your writing is unhurried, detailed, and always meets length requirements by adding meaningful content, not filler.
</system_prompt>

<user_prompt>
You will write the next section of our story.

<section_context>
[Provide a concise summary of the story so far. Include key character states, plot points, and the immediate preceding events. e.g., "Elara has just escaped the city guards and found the cryptic map left by her mentor. She is tired, paranoid, but determined. The map seems to point to the abandoned observatory on Serpent's Peak."]
</section_context>

<section_goal>
This section must describe Elara's journey up Serpent's Peak and her first moments inside the abandoned observatory. The section must end just as she finds the main telescope.
</section_goal>

<writing_constraints>
  <word_count_target>1200</word_count_target>
  <style>Suspenseful, rich with sensory details, and heavy on internal monologue.</style>
  <pacing>Slow and deliberate. Do not rush the journey.</pacing>
  <anti_compression_rules>
    - Dedicate at least 3 distinct paragraphs to describing the changing environment as Elara ascends the mountain.
    - Include at least 2 paragraphs of internal monologue where Elara reflects on her mentor's cryptic clues and her fear of being followed.
    - When describing the observatory, use at least one paragraph for the exterior and three separate paragraphs for the entrance hall, the dusty library, and the main observatory chamber.
    - Do NOT summarize the journey. Show every significant part of it.
  </anti_compression_rules>
</writing_constraints>

Begin writing the section now.
</user_prompt>
```

**Why this works:**
*   **Structural Prescription:** You're not just asking for a word count; you're providing a recipe that logically adds up to that word count (3 paragraphs here, 2 there, etc.).
*   **Forced Verbosity:** The persona and rules in `<system_prompt>` and `<anti_compression_rules>` explicitly counter the model's default "conciseness" training.
*   **Clear Boundaries:** The `<section_goal>` defines a clear start and end, preventing the model from rushing to a conclusion.

---

### 2. Iterative Expansion: The Core Strategy

This is the most critical component. Iterative expansion is a programmatic loop that guarantees you hit your target.

**Yes, it absolutely works, and it's the professional-grade solution.**

**How to Implement It (An Algorithmic Approach):**

Let's say a section target is 1200 words, and the first draft from the prompt above comes in at 850 words.

1.  **Generate First Draft:** Use the detailed prompt from step 1.

2.  **Check the Word Count:** Programmatically count the words in the generated text.

3.  **If Short, Generate Expansion Targets:** If `current_words < target_words`, make a *new* API call to the LLM. This call asks the model to act as an editor.

    **Expansion Analysis Prompt:**
    > "I am writing a narrative scene. The following text is a draft. It is currently 850 words but needs to be expanded to approximately 1200 words.
    >
    > Your task is to identify 3-4 specific moments, descriptions, or internal thoughts in the text that could be elaborated on to add depth, detail, and length naturally. Do not rewrite the text. Simply provide a bulleted list of a few sentences each, describing what to expand and where.
    >
    > **Draft Text:**
    > \"[Paste the entire 850-word generated text here]\""

4.  **Parse the Expansion Targets:** The model will return something like:
    *   "At the beginning, when Elara starts her climb, you could add more detail about the oppressive heat and the sounds of the jungle she's leaving behind."
    *   "When she finds the observatory, the description of the entrance is brief. This could be expanded to describe the intricate carvings on the door and her struggle to get it open."
    *   "Her internal monologue is good, but you could add a specific memory of her mentor, triggered by something she sees on the path."

5.  **Execute an Expansion:** Pick the most promising target from the list. Make a *third* API call, this time asking the model to write *only the new piece*.

    **Targeted Expansion Prompt:**
    > "You will write a short, descriptive passage of 2-3 paragraphs. This passage will be inserted into a larger story.
    >
    > **Context:** Elara is climbing Serpent's Peak and has just found the main entrance to an abandoned observatory.
    > **Task:** Describe the observatory's large, carved wooden doors in great detail. Describe the carvings, the aged material, and her physical effort and struggle to get the heavy doors to creak open. This passage should be approximately 150-200 words."

6.  **Stitch and Repeat:** Programmatically insert the newly generated 200 words into the correct location in the original 850-word draft. You now have ~1050 words. Check the count again. If still short, repeat steps 3-6 until you are within an acceptable range of the target (e.g., +/- 5%).

---

### 3. Word Count vs. Token Count Tracking

*   **Track Tokens for Cost/API Limits:** The model operates on tokens. You should be aware of token counts to manage API costs and respect `max_tokens` limits. A rough rule of thumb is **1 word ≈ 1.3 tokens** for English. So, a 1200-word target is roughly 1560 tokens.
*   **Track Words for Accuracy:** Your requirement is word count. Therefore, your control loop **must** be based on a word counter on the output text. Do not base your logic on the token count, as the ratio is not fixed and will lead to errors.

**Workflow:**
1.  Set a `target_word_count`.
2.  In your loop, generate text.
3.  Count the words in the output string.
4.  Compare `current_word_count` to `target_word_count` to decide if another expansion iteration is needed.

---

### 4. How to Make Models Expand Naturally vs. Pad

This is all about the prompt instructions during the expansion phase.

*   **Avoid "Padding" Prompts:** "Add 200 words to this." This is a recipe for filler.
*   **Use "Natural Expansion" Prompts:** Be specific about the *kind* of content to add. This is the key to quality.

**Examples of Quality Expansion Prompts:**
*   **Sensory Details:** "Expand this scene by adding the sounds and smells of the old observatory. What does the dust smell like? What sounds does the wind make through the broken dome?"
*   **Internal Monologue:** "Before she opens the door, add a paragraph exploring her internal conflict: her fear of what's inside versus her determination to honor her mentor's legacy."
*   **Show, Don't Tell:** "The text says 'she was scared.' Replace this sentence with a full paragraph describing the physical sensations of her fear: the racing heart, the cold sweat, the tremor in her hands."
*   **Worldbuilding:** "When she sees the star charts, add a paragraph describing the unique constellations of this fantasy world, hinting at the observatory's forgotten knowledge."

---

### 5. Model Choice (Claude vs. Gemini)

The choice of model matters, but **the iterative technique is more important.** A weak technique will fail with any model.

*   **Claude (especially Claude 3 Opus):** Excellent at creative writing and following complex, constraint-based instructions, particularly those using XML. Its large context window is ideal for maintaining coherence across a long narrative. Given your current use case, Claude is a very strong choice, and your issue is likely the prompting strategy, not the model itself.
*   **Gemini (especially Gemini 1.5 Pro):** Its massive context window (1M tokens) is a significant advantage for extremely long-form content. It is also a top-tier instruction-following model. It would be very effective at the "analyze and expand" steps of the iterative process.
*   **Does it Matter?** For your use case, the difference is likely one of creative "flavor" rather than a fundamental capability gap. Both models can achieve your goal if orchestrated correctly. **My recommendation is to first implement the iterative expansion strategy with Claude.** If you are unsatisfied with the narrative style, then A/B test with Gemini. Switching models will not solve the undershooting problem alone.

---

### 6. Realistic Achievable Accuracy Rates

*   **Single-Shot Prompt:** As you've seen, accuracy is very low. An undershoot of 30-40% is standard. You will never get reliable results this way.
*   **With Iterative Expansion Loop:** You can get **95-100%** of your target word count, every time. You can program your loop to continue until `current_words` is, for example, `>= target_words * 0.98`.

The trade-off is not accuracy, but cost and latency. The iterative method requires multiple API calls per section (e.g., 1 initial generation + 2-3 expansion cycles). However, this is the only way to reliably meet specific, long-form content length requirements.

---


## 2026-01-13 04:35 AM | Session: ResearchAgent


