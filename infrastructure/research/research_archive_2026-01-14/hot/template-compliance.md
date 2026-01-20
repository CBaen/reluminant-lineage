---
topic: "template-compliance"
category: "gemini"
tier: "hot"
tags:
  - "templates"
  - "markdown"
  - "structure"
  - "compliance"
created: "2026-01-11 04:37 PM"
last_accessed: "2026-01-11 04:37 PM"
access_count: 1
---

## 2026-01-11 04:37 PM | Session: ResearchAgent

Loaded cached credentials.
Excellent question. Using Markdown for research files, when combined with simple automation, can significantly improve template compliance and create a more consistent, manageable body of research. Here are the best practices and patterns that work well.

### 1. Enforcing Structure and Metadata with YAML Front Matter

The most critical practice is to use a **YAML front matter** block at the top of every Markdown file. This block contains key-value metadata that is easily machine-readable.

**Best Practice:** Define a strict, required set of metadata fields.

**Example `template.md`:**

```markdown
---
title: "Title of the Research Study"
author: "Your Name"
date: YYYY-MM-DD
project: "Project Name"
status: "draft" | "in-progress" | "review" | "completed"
tags: ["tag1", "tag2"]
---

# Abstract

...

# Introduction

...
```

**How this improves compliance:**

*   **Consistency:** Every document starts with the same, predictable metadata.
*   **Validation:** It's easy to write a script to check if all required fields (`title`, `author`, `status`, etc.) are present.
*   **Discoverability:** The metadata can be parsed to create automated indexes, dashboards, or search filters (e.g., "show me all studies with `status: 'completed'`").

---

### 2. Standardizing Content with a Template Structure

Beyond metadata, the body of the document should follow a consistent order of sections.

**Best Practice:** Create a `template.md` or a "research boilerplate" in a central repository that researchers can easily copy. The template should include the standard headings.

**Example Sections:**

*   **Abstract/Summary:** A brief overview of the research.
*   **Hypothesis / Research Question:** The core question being investigated.
*   **Methodology:** How the research was conducted.
*   **Data & Analysis:** Raw data (or links to it) and how it was analyzed.
*   **Results / Findings:** Key outcomes and observations.
*   **Discussion:** Interpretation of the findings.
*   **Next Steps / Future Work:** What this research enables.

---

### 3. Automating Validation and Formatting

This is the key to *enforcing* the standards. Manual checks don't scale.

**Best Practices & Patterns:**

*   **Markdown Linting (`markdownlint`):** Use a tool like `markdownlint` to enforce formatting standards automatically. This can check for things like:
    *   Consistent heading styles (`#` vs `##`).
    *   Proper list formatting.
    *   Line length.
    *   A rule can even enforce the presence of top-level headings like `Abstract` and `Methodology`.
    *   **Implementation:** Run this as a **pre-commit git hook**. This prevents poorly formatted files from ever entering the repository.

*   **Metadata Validation Scripts:**
    *   Write a simple script (Python, Node.js, or even a shell script using `yq` or similar tools) that:
        1.  Finds all new/modified `.md` files in a commit.
        2.  Parses the YAML front matter.
        3.  Checks that all required keys are present.
        4.  Validates the values (e.g., `date` is a valid date, `status` is one of the allowed options).
    *   **Implementation:** Also run this as a **pre-commit git hook**. If validation fails, the commit is aborted with a clear error message telling the researcher what to fix.

*   **CI/CD Pipeline Checks:** For larger teams, these same linting and validation scripts can be run in a continuous integration (CI) pipeline (e.g., using GitHub Actions). This acts as a secondary check and is essential for enforcing standards on a shared repository.

---

### 4. Patterns for Ensuring Predictable Templates

*   **The "Living Document" Pattern:**
    *   A single research file is created at the start of an investigation with `status: 'draft'`.
    *   The researcher updates the *same file* as the work progresses, moving the `status` through `in-progress`, `review`, and finally to `completed`.
    *   This creates a predictable lifecycle and avoids scattered, duplicative files. The git history for that single file tells the story of the research.

*   **The "Static Site Generator" (SSG) Incentive:**
    *   Use a tool like **Hugo**, **Jekyll**, or **Docusaurus** to automatically build an internal research website from the Markdown files.
    *   These tools natively understand YAML front matter and can use it to build indexes, author pages, and tag clouds automatically.
    *   **This provides a powerful incentive for compliance:** if your Markdown file doesn't follow the template, it will render incorrectly or not show up on the website. This immediate feedback loop encourages proper formatting more effectively than just a failed CI check.

By combining a clear template with automated validation (especially via git hooks), you create a system where following the standard is the path of least resistance, leading to a highly consistent and valuable research archive.
