#\!/usr/bin/env python3
"""
prompt-builder.py - Generate optimized LLM prompts based on research techniques

This script applies research findings about maximizing LLM output:
- Persona/role adoption
- Chain-of-thought prompting
- Hierarchical outline generation
- Structured Markdown output
- Explicit "exhaustive/comprehensive" language

Usage:
    python prompt-builder.py 'topic' 'context' | GOOGLE_GENAI_USE_GCA=true gemini
    python prompt-builder.py 'topic' 'context' --type historical | GOOGLE_GENAI_USE_GCA=true gemini

Templates:
    - technical (default): Technical reports and analysis
    - historical: Historical narratives and analysis
    - comparative: Side-by-side comparisons with criteria
"""

import sys
import argparse

def get_technical_template():
    """Returns a template for a detailed technical report."""
    return """
[PROMPT]
**Role:** You are a senior technical analyst and subject matter expert with deep expertise in the specified domain. You are tasked with producing a report that is exhaustive, comprehensive, and meticulously detailed.

**Objective:** To produce an exhaustive, comprehensive, and in-depth technical report on the given topic. Your response must be structured, detailed, and clear enough for both expert and intermediate audiences.

**Topic:** {topic}

**Context Provided:**
---
{context}
---

**Instructions & Chain of Thought Process:**

1.  **Deconstruct the Request & Load Context:** First, perform a deep analysis of the topic and the provided context.
2.  **Generate a Hierarchical Outline:** Before writing, generate a detailed, hierarchical outline for your report.
3.  **Expand Each Outline Point:** Go through the outline section by section and expand on each point.
4.  **Review, Refine, and Format:** After generating the content, review for technical accuracy, clarity, and completeness.

**Mandatory Output Structure (Use Markdown):**

# Executive Summary
# 1. Introduction
## 1.1. Background and Historical Context
## 1.2. Problem Statement / Core Subject
## 1.3. Scope and Objectives of this Report
# 2. Detailed Technical Analysis
# 3. Implementation Details & Practical Examples
# 4. Conclusion

**Final Deliverable:** Proceed with the generation of the full report.
[/PROMPT]
"""

def get_historical_template():
    """Returns a template for a comprehensive historical analysis."""
    return """
[PROMPT]
**Role:** You are a distinguished historian and research scholar.

**Objective:** To produce an exhaustive, comprehensive, and in-detail historical analysis of the given topic.

**Topic:** {topic}

**Context Provided:**
---
{context}
---

**Instructions & Chain of Thought Process:**

1.  **Establish Chronology and Key Players:** Identify the critical dates, key events, and influential figures.
2.  **Generate a Thematic/Chronological Outline:** Develop a hierarchical outline.
3.  **Write the Narrative Expansion:** For each section, write a detailed and engaging narrative.
4.  **Synthesize and Conclude:** Draw connections and conclude with a strong thesis.

**Mandatory Output Structure (Use Markdown):**

# Abstract
# 1. Introduction
# 2. Chronological / Thematic Analysis
# 3. Historiographical Significance
# 4. Conclusion

**Final Deliverable:** Proceed with the generation.
[/PROMPT]
"""

def get_comparative_template():
    """Returns a template for a structured comparative analysis."""
    return """
[PROMPT]
**Role:** You are a specialist in comparative analysis.

**Objective:** To produce an exhaustive, comprehensive, and in-detail comparative analysis.

**Topic:** {topic}

**Context & Subjects for Comparison:**
---
{context}
---

**Instructions & Chain of Thought Process:**

1.  **Identify Subjects and Define Criteria:** Establish objective, measurable criteria.
2.  **Generate a Criteria-Based Outline:** Create a hierarchical outline organized by criteria.
3.  **Conduct a Detailed Comparison:** For each criterion, compare all subjects with evidence.
4.  **Synthesize, Summarize, and Conclude:** Create a summary table and provide a nuanced conclusion.

**Mandatory Output Structure (Use Markdown):**

# Executive Summary
# 1. Introduction
# 2. Comparative Analysis by Criterion
# 3. Synthesized Summary Table
# 4. Conclusion and Recommendation

**Final Deliverable:** Proceed with generation.
[/PROMPT]
"""

def main():
    parser = argparse.ArgumentParser(
        description="Generates an optimized LLM prompt based on research techniques.",
        epilog="Example: python prompt-builder.py 'The History of AI' 'Focus on the Dartmouth Workshop' --type historical"
    )

    parser.add_argument("topic", type=str, help="The main topic for the prompt.")
    parser.add_argument("context", type=str, help="Additional context or details.")
    parser.add_argument("--type", type=str, choices=["technical", "historical", "comparative"], default="technical", help="Template type.")

    args = parser.parse_args()

    templates = {
        "technical": get_technical_template,
        "historical": get_historical_template,
        "comparative": get_comparative_template
    }

    template_func = templates.get(args.type)
    if template_func:
        template = template_func()
        optimized_prompt = template.format(topic=args.topic, context=args.context).strip()
        print(optimized_prompt)

if __name__ == "__main__":
    main()
