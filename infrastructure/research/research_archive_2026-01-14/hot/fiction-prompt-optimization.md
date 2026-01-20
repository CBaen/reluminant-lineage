---
topic: "fiction-prompt-optimization"
category: "gemini"
tier: "hot"
tags:
  - "llm-writing"
  - "prompt-structure"
  - "fiction-generation"
  - "episode-forge"
  - "llm-writing"
  - "prompt-structure"
  - "fiction-generation"
  - "episode-forge"
created: "2026-01-13 04:35 AM"
last_accessed: "2026-01-13 04:59 AM"
access_count: 2
---

## 2026-01-13 04:59 AM | Session: ResearchFix

Loaded cached credentials.
This is an excellent research question that gets to the heart of effectively collaborating with LLMs for complex creative tasks. Based on current prompt engineering best practices, here is a breakdown of the optimal prompt structure for generating long-form fiction.

### Executive Summary

For long-form fiction (5K-15K words), the optimal strategy is **not a single prompt**. It is an iterative, **section-by-section approach** using **Markdown** for structure. Key constraints, persona, and world-building rules should be **front-loaded in a "master" prompt**, and a summary of the story so far must be included in each subsequent sectional prompt to maintain coherence.

---

### 1. Structure Format: XML vs. Markdown vs. Plain Text

**Winner: Markdown**

*   **Markdown:** This is the most effective format. LLMs have seen vast quantities of Markdown in their training data (wikis, technical docs, forum posts). It provides clear, hierarchical structure (`# Chapter`, `## Scene`, `- Character Trait`) without the verbosity of XML. It is human-readable and easy to write. The structure helps the model delineate concepts and instructions clearly.

*   **XML:** While LLMs understand XML perfectly, it is often overkill. Its main advantage is unambiguous nesting, which can be useful for extremely complex prompts with metadata (e.g., `<character id="001"><name>John</name><arc>redemption</arc></character>`). However, for narrative fiction, the syntax is clunky and adds unnecessary token overhead. It is a "power user" tool but not the most efficient.

*   **Plain Text:** This is the weakest option for long-form. It forces the LLM to infer structure from prose, which can lead to misinterpretation. Instructions can get lost in the sea of text. It's fine for short, simple requests but lacks the robustness needed for a multi-thousand-word project.

### 2. Constraint Placement: Beginning vs. End vs. Inline

**Winner: Primarily at the beginning, with inline for specific scenes.**

*   **Beginning (The "Preamble"):** This is the most critical placement. All global rules, stylistic guides, persona instructions, character sheets, and plot outlines should be placed at the very top of the prompt. LLMs give the most weight to initial instructions. This sets the "rules of the game" before any generation begins, ensuring the entire output is framed correctly.

*   **Inline (In-context):** These are for section-specific instructions. Use them to guide the immediate output. For example, after providing the summary of Chapter 1, you might instruct: `For this next scene, focus entirely on Sarah's internal monologue. Do not include dialogue from other characters. Emphasize the sensory details of the rainy street.`

*   **End:** Placing constraints at the end is the least effective method. The model may have already "decided" on its generation path and may treat trailing instructions as an afterthought or ignore them completely. It's like giving a director notes after the scene has already been filmed.

### 3. Anti-Compression & Pacing Rules

LLMs are natural summarizers. To force long-form, detailed output, you must be explicit.

*   **Use Both Positive and Negative Constraints:**
    *   **Negative:** "Do not summarize.", "Do not conclude the story.", "Do not skip ahead in time.", "Avoid short, simple paragraphs."
    *   **Positive:** "Write at least 1,200 words for this chapter.", "Each paragraph must contain at least five sentences.", "Elaborate on the character's emotions and internal thoughts in detail."

*   **Focus on Process and Detail:**
    *   Instead of just asking for length, guide the *process* of creating that length.
    *   **Good:** "Describe the marketplace scene, focusing on the sights, sounds, and smells."
    *   **Better:** "Write the marketplace scene. Dedicate one paragraph to the smell of the spice vendors. Dedicate a second paragraph to the sound of the crowd haggling. Dedicate a third paragraph to the visual of the brightly colored fabrics."

*   **"Show, Don't Tell" as a Command:** Explicitly instruct the model to "Show, don't tell." Provide an example if necessary. "Instead of saying 'she was scared,' describe her heart pounding, the sweat on her palms, and her darting eyes."

### 4. Persona/Role-Play Instructions

A well-defined persona is one of the most powerful tools for improving narrative quality. It moves the LLM from a generic text generator to a stylized author.

*   **Weak Persona:** "Act as a fiction writer."
*   **Good Persona:** "Act as a science-fiction author in the style of Isaac Asimov."
*   **Optimal Persona:** "Adopt the persona of a master storyteller in the hardboiled detective genre of the 1940s, in the vein of Raymond Chandler. Your prose must be cynical, terse, and full of vivid, world-weary metaphors. Use short, punchy sentences and focus on atmospheric descriptions of the rain-slicked city streets. The protagonist's internal monologue should be jaded and observational."

The key is to provide:
1.  **A Genre/Archetype:** (Hardboiled detective, epic fantasy chronicler)
2.  **A Stylistic Analog:** (In the vein of..., reminiscent of...)
3.  **Specific Prose Rules:** (Use short sentences, focus on sensory details, employ metaphors)

### 5. Section-by-Section vs. Single-Shot Generation

**Winner: Section-by-Section is the only viable method for 5K+ words.**

*   **Single-Shot:** This will fail. Even with a large context window, an LLM tasked with writing 10,000 words in one go will inevitably rush the plot, lose track of characters and details, and write a hasty, summarized conclusion. The quality degrades sharply over extremely long, unguided generations.

*   **Section-by-Section (Iterative):** This is the professional workflow. It treats the LLM as a collaborator.
    1.  **Start** with a "Master Prompt" containing all global rules and the request for Chapter 1.
    2.  **For Chapter 2,** create a new prompt. This prompt *must* include:
        *   The original Persona, Style, and Core Plot rules.
        *   A new section: `## Story So Far`, containing a concise summary of Chapter 1.
        *   The specific task: `Now, write Chapter 2, focusing on...`
    3.  **Repeat** this process for every chapter. The `Story So Far` section is critical; it is the context-carrier that ensures continuity. This method also allows you to course-correct the plot as you go.

---

### Practical Prompt Templates

#### Template 1: The "Master" Initial Prompt

```markdown
# Persona
Adopt the persona of a seasoned epic fantasy author, in the style of Ursula K. Le Guin. Your prose is elegant, intelligent, and philosophical. You focus on character psychology, societal structures, and the quiet moments between big events. Your tone is more "low fantasy" and grounded, avoiding overly bombastic action.

# Core World Rules & Setting
- **World:** The world of Aerthos is in an early industrial age, but with remnant magic. Magic is fading and seen as unreliable.
- **Technology:** Steam-powered engines exist alongside horse-drawn carts. There are no firearms.
- **Setting for this story:** The smog-filled, stratified capital city of Cinderfall.

# Main Characters
- **Kaelen:** A young, pragmatic factory worker who has discovered he has a spark of the fading magic. He is cautious and frightened of his abilities.
- **Lady Elara:** An aristocratic scholar who studies the history of magic. She is intellectually curious but naive about the struggles of the lower class.

# High-Level Plot Outline
1.  Kaelen discovers his magic.
2.  He accidentally causes a public magical event, attracting the attention of the authorities and Elara.
3.  Elara seeks him out to study him; he is wary of her.
4.  They form an uneasy alliance to understand why his magic is so strong when all other magic is fading.
5.  They uncover a secret that the city's industrial engines are actively draining magic from the world.

# Stylistic & Anti-Compression Rules
- **Pacing:** This is a slow-burn story. Focus on detailed descriptions and internal monologue.
- **Length:** Each chapter should be approximately 1,500 words.
- **Prohibition:** Do NOT summarize. Do NOT conclude the story. Do NOT rush the plot.
- **Detail:** When describing a scene, dedicate at least one paragraph to the environment before focusing on character actions. Show, don't tell.

# Task
Write Chapter 1 of this story. In this chapter, Kaelen is finishing a long shift at the steam-foundry. While walking home through a crowded, grimy street, a cart almost runs over a child. Without thinking, Kaelen instinctively uses magic for the first time to stop it, diverting it into a wall with a telekinetic shove. He is terrified and confused by what he has done and flees the scene.
```

#### Template 2: The Iterative "Chapter 2+" Prompt

```markdown
# Persona
(Repeat the full persona from the master prompt)
Adopt the persona of a seasoned epic fantasy author, in the style of Ursula K. Le Guin...

# Core World Rules & Setting
(Repeat from the master prompt)

# Main Characters
(Repeat from the master prompt)

# High-Level Plot Outline
(Repeat from the master prompt)

# Stylistic & Anti-Compression Rules
(Repeat from the master prompt)

# Story So Far
In Chapter 1, Kaelen, a factory worker in the industrial city of Cinderfall, discovered he has latent magic. After a grueling shift, he unconsciously used telekinesis to stop a runaway cart from hitting a child. The event was public, and he fled the scene in a state of terror and confusion about his newfound abilities.

# Task
Write Chapter 2 of this story (approx. 1,500 words). In this chapter, we introduce Lady Elara. She is in her study at the upper-city Athenaeum, reading historical texts about the decline of magic. Her research is interrupted by a city constable who reports the strange incident with the cart, describing it as a powerful and rare manifestation of raw magic. Intrigued, Elara decides she must find the person responsible.

**Inline Constraint for this Chapter:** When describing Elara's study, focus on the contrast between her orderly, quiet world of books and the chaotic, industrial city outside her window.
```

---


## 2026-01-13 04:35 AM | Session: ResearchAgent


