---
topic: "gemini-prompt-engineering"
category: "gemini"
tier: "hot"
tags:
  - "gemini"
  - "prompt-engineering"
  - "llm"
  - "system-prompts"
  - "advanced-techniques"
  - "token-optimization"
created: "2026-01-11 05:57 PM"
last_accessed: "2026-01-11 05:57 PM"
access_count: 1
---

## 2026-01-11 05:57 PM | Session: ResearchAgent

Loaded cached credentials.
Error executing tool write_file: Tool "write_file" not found in registry. Tools must use the exact names that are registered. Did you mean one of: "read_file", "write_todos", "glob"?
I have gathered comprehensive information on best practices for prompt engineering with Google Gemini. I will now create a detailed guide in a markdown file.
Error executing tool write_file: Tool "write_file" not found in registry. Tools must use the exact names that are registered. Did you mean one of: "read_file", "write_todos", "glob"?
I apologize for the repeated errors. I will now output the content of the guide directly.

# Best Practices for Prompt Engineering with Google Gemini

This guide provides comprehensive best practices for prompt engineering with Google Gemini models. It covers system instructions, parameter tuning, token optimization, and advanced prompting techniques to help you get the most out of Gemini.

## 1. System Instructions

System instructions (or a system prompt) set the context and rules for the model's behavior throughout a conversation. A well-crafted system instruction is critical for guiding the model's persona, response format, and constraints.

### How to Structure Them for Gemini

Gemini models respond best to direct, clear, and specific instructions. Unlike other models that might respond to more conversational or persuasive language, Gemini favors a logical and straightforward structure.

- **Be Direct and Unambiguous:** State your requirements clearly. Avoid fuzzy or vague language.
- **Use Structural Delimiters:** Use Markdown (like `##` headings) or XML-style tags (like `<context>`) to logically separate different parts of your prompt, such as persona, task, context, and format. Do not mix styles within the same prompt.
- **Prioritize Key Instructions:** Place the most critical instructions—like the model's persona, core task, and essential "do-nots"—at the very top of the system prompt.
- **Provide Context First, Instructions Last:** For long prompts with a lot of reference material (e.g., a long document to summarize), place the content first and the specific instruction or question at the very end.

### Differences from Claude and GPT

- **Gemini vs. Claude:** Claude has been specifically fine-tuned to respond well to **XML tags** (`<example>`, `<context>`). While Gemini can understand them, it doesn't have the same explicit preference. With Gemini, consistency in structure (whether Markdown or XML) is more important than the specific choice of delimiter.
- **Gemini vs. GPT:** GPT models are also highly responsive to structured prompts. A common pattern is using `###` as a delimiter. Gemini is similar but often performs better with even more direct and less "chatty" instructions. Gemini 3 models, in particular, are less verbose by default, so if you need detailed output, you must explicitly ask for it.

### Example

**Before (Less Effective for Gemini):**
> "Hey there! Would you mind acting like a super-friendly and helpful financial expert? I'm going to give you some stock data, and I'd love it if you could analyze it for me and tell me which one looks like the best investment. Be really smart about it, okay?"

**After (More Effective for Gemini):**
```markdown
## Persona
You are a professional financial analyst. Your tone is formal, objective, and data-driven. Do not provide financial advice. Your analysis should be based solely on the data provided.

## Task
Analyze the provided stock data. For each stock, calculate the percentage change in price over the given period. Identify the stock with the highest volatility based on price fluctuations.

## Output Format
Return your analysis in a JSON object with the following structure for each stock:
{
  "ticker": "string",
  "percentage_change": "float",
  "volatility_assessment": "string (e.g., 'High', 'Medium', 'Low')"
}
```

---

## 2. Temperature and Top-P Settings

`temperature` and `top_p` are two key parameters that control the randomness and diversity of the model's output.

- **Temperature:** Controls the randomness of token selection. A higher value (e.g., 1.2) leads to more creative and unexpected outputs, while a lower value (e.g., 0.2) makes the output more deterministic and focused.
- **Top-P (Nucleus Sampling):** Controls the diversity of the output by selecting from a smaller, more probable set of tokens. It creates a "nucleus" of the most likely tokens whose cumulative probability mass adds up to the `top_p` value. A higher value (e.g., 0.95) allows for more diversity.

It is generally recommended to **modify only one of these parameters**, not both.

### Recommended Values by Task Type

| Task Type             | Temperature | Top-P   | Use Case                                   |
| --------------------- | ----------- | ------- | ------------------------------------------ |
| **Precise / Factual** | 0.0 - 0.4   | 0.2-0.5 | Code generation, data extraction, summarization |
| **Balanced / General**| 0.5 - 0.7   | 0.6-0.9 | General writing, brainstorming, conversation |
| **Creative**          | 0.8 - 1.5   | 0.9-1.0 | Story writing, poetry, marketing copy      |

### Gemini-Specific Quirks

For some Gemini models, especially in complex reasoning tasks, Google recommends keeping the **`temperature` at its default value (often 1.0)**. Altering it can sometimes lead to degraded performance. If you need more predictable output for reasoning tasks, consider lowering `top_p` first before adjusting temperature.

---

## 3. Token Optimization (Prompt Compression)

Token optimization reduces the length of your prompt, which saves costs and can improve performance, especially in long-context scenarios where models can suffer from the "lost in the middle" problem.

### Techniques

- **Semantic Summarization:** Condense long texts into shorter summaries that retain the core meaning.
- **Structured Formats:** Use compact formats like JSON or bullet points instead of verbose sentences.
- **Abbreviations and Symbols:** Develop a shorthand for long, repetitive phrases or instructions.
- **Instructional Layering:** For complex workflows, break instructions into smaller prompts instead of one massive one.

### Example

**Verbose Prompt (~60 tokens):**
> "Please analyze the following user feedback. The feedback is: 'The app is really slow to load on my phone and it keeps crashing whenever I try to open the settings page.' I want you to categorize this feedback into one of two categories: 'Performance' or 'Stability'. Then, identify the key issue being described."

**Compressed Prompt (~30 tokens):**
```json
{
  "task": "categorize_and_extract",
  "text": "The app is really slow to load on my phone and it keeps crashing whenever I try to open the settings page.",
  "categories": ["Performance", "Stability"],
  "output_format": {
    "category": "string",
    "key_issue": "string"
  }
}
```

---

## 4. Few-shot vs. Zero-shot Prompting

### Zero-Shot Prompting

This is the most basic form of prompting, where you ask the model to perform a task without giving it any prior examples.

- **When to use:** Simple, common tasks that the model has likely seen during its training (e.g., general summarization, simple sentiment analysis, answering common questions).
- **Example:**
> **Prompt:**
> Classify the following text's sentiment as 'Positive', 'Negative', or 'Neutral'.
>
> Text: "I'm not thrilled with the new update."
>
> **Output:**
> Negative

### Few-Shot Prompting (In-Context Learning)

This technique involves providing the model with a few examples (`shots`) of the task you want it to perform. This helps the model understand the desired output format, style, and reasoning process.

- **When to use:** Complex tasks, tasks requiring a specific output format, or nuanced classification/extraction tasks.
- **Best Practices:**
    - Use at least 2-3 examples.
    - Ensure the examples are high-quality and consistent in their format.
    - The structure of your examples should mirror the final task.

- **Example:**
> **Prompt:**
> Extract the company name and the specific product mentioned from the text. If no product is mentioned, use "N/A".
>
> **Text:** "I love using Google Docs for all my writing."
> **Company:** Google
> **Product:** Docs
>
> **Text:** "The new MacBook is amazing, but Apple's pricing is high."
> **Company:** Apple
> **Product:** MacBook
>
> **Text:** "I just bought a new shirt from a local store."
> **Company:** N/A
> **Product:** N/A
>
> **Text:** "Microsoft Excel is powerful but has a steep learning curve."
>
> **Output:**
> **Company:** Microsoft
> **Product:** Excel

---

## 5. Advanced Techniques

### Chain-of-Thought (CoT)

CoT prompting encourages the model to break down a complex problem into intermediate steps before giving a final answer. This dramatically improves performance on tasks requiring arithmetic, commonsense, or symbolic reasoning.

- **Zero-Shot CoT:** Simply add the phrase **"Let's think step by step."** or **"Break this down and solve it step-by-step."** to your prompt.
- **Few-Shot CoT:** Provide examples that include the reasoning steps.

- **Example (Few-Shot CoT):**
> **Prompt:**
> Q: John has 5 apples. He buys 2 more boxes of apples, and each box contains 6 apples. He then gives 3 apples to his friend. How many apples does John have left?
>
> A:
> 1. John starts with 5 apples.
> 2. He buys 2 boxes of 6 apples, so he gets 2 * 6 = 12 more apples.
> 3. His total is now 5 + 12 = 17 apples.
> 4. He gives away 3 apples.
> 5. He has 17 - 3 = 14 apples left.
> The final answer is 14.
>
> Q: A car travels at 60 mph for 30 minutes. It then travels at 40 mph for 15 minutes. What is the total distance the car has traveled?

### Self-Consistency

Self-consistency builds on CoT to improve accuracy further. It works by generating multiple different reasoning paths (by using a higher `temperature`) and then choosing the most consistent answer from the results.

- **Workflow:**
    1.  Use a CoT prompt for a complex problem.
    2.  Set the `temperature` to a higher value (e.g., 0.7 or higher).
    3.  Generate multiple (e.g., 3 to 5) responses for the same prompt.
    4.  Extract the final answer from each response and choose the one that appears most frequently (i.e., the consensus answer).

- **Example Prompt:**
> "Solve the following problem. Show your work, and provide the final numerical answer at the end.
>
> Problem: [Insert complex problem here]
>
> Provide three different and unique ways to arrive at the solution."

### Tree-of-Thoughts (ToT)

ToT is a more advanced framework that generalizes CoT. Instead of a single chain, it explores a "tree" of possible reasoning steps. At each step, it generates multiple "thoughts" (potential next steps) and uses self-reflection or a search algorithm to decide which path to pursue.

Implementing a full ToT framework often requires external code to manage the "tree" of responses. However, you can simulate the core idea by prompting Gemini to perform the steps explicitly.

- **Conceptual Example Prompt:**
> "I need to solve this logic puzzle.
>
> Puzzle: [Insert puzzle here]
>
> 1.  **Generate 3 potential starting points** for solving this puzzle.
> 2.  **Evaluate each starting point:** For each one, write a short critique of its pros and cons as a first step.
> 3.  **Choose the best starting point** based on your evaluation.
> 4.  **From the best starting point, generate the next 2 steps** and evaluate them.
> 5.  Continue this process until you reach the final solution."

This approach guides the model to explore, evaluate, and backtrack, simulating a ToT-like reasoning process.
