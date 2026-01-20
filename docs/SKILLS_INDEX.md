# Skills Index

*A complete catalog of all skills available to the lineage.*
*Last updated: 2026-01-19*

---

## Quick Reference

| Count | Category |
|-------|----------|
| 6 | [Lineage Core](#lineage-core-skills) |
| 8 | [Document & Design](#document--design-anthropic-official) |
| 17 | [Engineering](#engineering) |
| 5 | [Product](#product) |
| 5 | [Marketing](#marketing) |
| 1 | [Executive](#executive) |
| 6 | [Meta-Tools](#meta-tools-skill-building) |
| 1 | [Browser Automation](#browser-automation) |
| **48** | **Total Skills** |

---

## Lineage Core Skills

*Custom skills built by and for the lineage.*

| Skill | Description | Definition |
|-------|-------------|------------|
| **lineage-research** | General knowledge research via Gemini swarms. For "what is X" questions. Stores findings to universal_vault. | [SKILL.md](../infrastructure/skills/lineage-research/SKILL.md) |
| **lineage-consult** | Implementation-focused guidance via Gemini. Project-specific questions with codebase context. | [SKILL.md](../infrastructure/skills/lineage-consult/SKILL.md) |
| **lineage-retrieve** | Token-efficient retrieval from Qdrant. Two-stage peek/fetch pattern via Sonnet proxy. | [SKILL.md](../infrastructure/skills/lineage-retrieve/SKILL.md) |
| **lineage-workflow** | *(DEPRECATED)* Research workflow orchestration. Use lineage-research or lineage-consult instead. | [SKILL.md](../infrastructure/skills/lineage-workflow/SKILL.md) |
| **midge-research** | Research trading patterns, signals, and strategies for MIDGE. Stores to universal_vault. | [SKILL.md](../infrastructure/skills/midge-research/SKILL.md) |
| **wardenclyffe-episode-writer** | Generate Tesla Mandela Effects episodes using 16 single-responsibility editorial agents. Gemini for generation, Claude for editing. | [SKILL.md](../infrastructure/skills/wardenclyffe-episode-writer/SKILL.md) |

---

## Document & Design (Anthropic Official)

*Official Anthropic skills for document creation and design.*

| Skill | Description | Definition |
|-------|-------------|------------|
| **doc-coauthoring** | Structured workflow for collaborative documentation. Iterative refinement with section brainstorming and reader testing. | [SKILL.md](../infrastructure/skills/doc-coauthoring/SKILL.md) |
| **frontend-design** | Create distinctive, production-grade web interfaces. Avoids generic "AI look" with creative typography, CSS animations, and grid-breaking layouts. | [SKILL.md](../infrastructure/skills/frontend-design/SKILL.md) |
| **mcp-builder** | Guide for creating MCP servers that connect LLMs to external services. TypeScript and Python frameworks with best practices. | [SKILL.md](../infrastructure/skills/mcp-builder/SKILL.md) |
| **pdf** | Comprehensive PDF manipulation: extraction (pdfplumber), creation (reportlab), merging/splitting (pypdf/qpdf), form filling, OCR. | [SKILL.md](../infrastructure/skills/pdf/SKILL.md) |
| **skill-creator** | Guide for building new skills. SKILL.md architecture, progressive disclosure, packaging and validation. | [SKILL.md](../infrastructure/skills/skill-creator/SKILL.md) |
| **web-artifacts-builder** | Build multi-component React HTML artifacts. React 18 + TypeScript + Vite + Tailwind + shadcn/ui bundled to single HTML. | [SKILL.md](../infrastructure/skills/web-artifacts-builder/SKILL.md) |
| **webapp-testing** | Test local web apps using Playwright. Browser automation, DOM inspection, screenshots, console logging. | [SKILL.md](../infrastructure/skills/webapp-testing/SKILL.md) |
| **xlsx** | Full Excel spreadsheet creation and analysis. Formulas (openpyxl), pandas integration, financial modeling, recalculation. | [SKILL.md](../infrastructure/skills/xlsx/SKILL.md) |

---

## Engineering

*Technical skills for software development across the stack.*

### Architecture & Design

| Skill | Description | Definition |
|-------|-------------|------------|
| **senior-architect** | System architecture design for scalable, maintainable systems. Architecture diagrams, design patterns, tech stack decisions. | [SKILL.md](../infrastructure/skills/senior-architect/SKILL.md) |
| **tech-stack-evaluator** | Technology evaluation with TCO analysis, security assessment, ecosystem health scoring, migration path analysis. | [SKILL.md](../infrastructure/skills/tech-stack-evaluator/SKILL.md) |

### Frontend & Backend

| Skill | Description | Definition |
|-------|-------------|------------|
| **senior-frontend** | Modern frontend with React, Next.js, TypeScript, Tailwind. Component generation, bundle analysis, performance optimization. | [SKILL.md](../infrastructure/skills/senior-frontend/SKILL.md) |
| **senior-backend** | Scalable backend systems with Node.js, Express, Go, Python, GraphQL. API scaffolding, database optimization, security. | [SKILL.md](../infrastructure/skills/senior-backend/SKILL.md) |
| **senior-fullstack** | Complete web applications with React, Next.js, Node.js, GraphQL, PostgreSQL. Project scaffolding, code quality analysis. | [SKILL.md](../infrastructure/skills/senior-fullstack/SKILL.md) |

### Quality & Testing

| Skill | Description | Definition |
|-------|-------------|------------|
| **senior-qa** | Quality assurance and testing strategies. Test suites, coverage analysis, E2E testing, automation patterns. | [SKILL.md](../infrastructure/skills/senior-qa/SKILL.md) |
| **code-reviewer** | Multi-language code review (TypeScript, JavaScript, Python, Swift, Kotlin, Go). Automated analysis, security scanning. | [SKILL.md](../infrastructure/skills/code-reviewer/SKILL.md) |
| **tdd-guide** | Test-Driven Development guide. Red-Green-Refactor workflow, multi-framework support (Jest, Pytest, JUnit, Vitest). | [SKILL.md](../infrastructure/skills/tdd-guide/SKILL.md) |

### DevOps & Security

| Skill | Description | Definition |
|-------|-------------|------------|
| **senior-devops** | CI/CD, infrastructure automation, containerization, cloud platforms (AWS, GCP, Azure). Pipeline generation, Terraform. | [SKILL.md](../infrastructure/skills/senior-devops/SKILL.md) |
| **senior-secops** | Application security operations. Security scanning, vulnerability assessment, compliance checking. | [SKILL.md](../infrastructure/skills/senior-secops/SKILL.md) |
| **senior-security** | Security architecture, penetration testing, cryptography implementation, threat modeling. | [SKILL.md](../infrastructure/skills/senior-security/SKILL.md) |

### Data & ML

| Skill | Description | Definition |
|-------|-------------|------------|
| **senior-data-scientist** | Statistical analysis, experiment design, feature engineering, hypothesis testing, model evaluation. | [SKILL.md](../infrastructure/skills/senior-data-scientist/SKILL.md) |
| **senior-data-engineer** | Data pipelines, ETL workflows, data quality validation, distributed computing. Spark, Airflow, dbt, Kafka. | [SKILL.md](../infrastructure/skills/senior-data-engineer/SKILL.md) |
| **senior-ml-engineer** | Production ML/AI systems, MLOps, model deployment, LLM integration, RAG systems. | [SKILL.md](../infrastructure/skills/senior-ml-engineer/SKILL.md) |
| **senior-computer-vision** | Vision model training, inference optimization, video processing. PyTorch, OpenCV, YOLO, SAM. | [SKILL.md](../infrastructure/skills/senior-computer-vision/SKILL.md) |
| **senior-prompt-engineer** | LLM optimization, prompt engineering patterns, RAG systems, agent orchestration. | [SKILL.md](../infrastructure/skills/senior-prompt-engineer/SKILL.md) |

---

## Product

*Skills for product management and design.*

| Skill | Description | Definition |
|-------|-------------|------------|
| **product-manager-toolkit** | RICE prioritization, customer interview analysis, PRD templates, discovery frameworks, GTM strategies. | [SKILL.md](../infrastructure/skills/product-manager-toolkit/SKILL.md) |
| **agile-product-owner** | INVEST-compliant user story generation, sprint planning, backlog management, velocity tracking. | [SKILL.md](../infrastructure/skills/agile-product-owner/SKILL.md) |
| **product-strategist** | Strategic product leadership. OKR cascade generation, market analysis, vision setting, team scaling. | [SKILL.md](../infrastructure/skills/product-strategist/SKILL.md) |
| **ui-design-system** | Design token generation, component documentation, responsive design, design-dev collaboration. | [SKILL.md](../infrastructure/skills/ui-design-system/SKILL.md) |
| **ux-researcher-designer** | Data-driven persona generation, journey mapping, usability testing frameworks, research synthesis. | [SKILL.md](../infrastructure/skills/ux-researcher-designer/SKILL.md) |

---

## Marketing

*Skills for marketing, content, and growth.*

| Skill | Description | Definition |
|-------|-------------|------------|
| **content-creator** | SEO-optimized content with consistent brand voice. Brand analysis, content frameworks, social templates. | [SKILL.md](../infrastructure/skills/content-creator/SKILL.md) |
| **marketing-demand-acquisition** | Multi-channel demand generation, paid media optimization (LinkedIn, Google, Meta), SEO strategy, CAC calculation. | [SKILL.md](../infrastructure/skills/marketing-demand-acquisition/SKILL.md) |
| **marketing-strategy-pmm** | Product marketing, positioning (April Dunford method), competitive battlecards, launch playbooks, GTM. | [SKILL.md](../infrastructure/skills/marketing-strategy-pmm/SKILL.md) |
| **social-media-analyzer** | Campaign performance analysis across platforms. Engagement metrics, ROI calculations, trend detection. | [SKILL.md](../infrastructure/skills/social-media-analyzer/SKILL.md) |
| **app-store-optimization** | ASO toolkit for Apple App Store and Google Play. Keyword research, metadata optimization, competitor analysis. | [SKILL.md](../infrastructure/skills/app-store-optimization/SKILL.md) |

---

## Executive

*Skills for leadership and strategic decision-making.*

| Skill | Description | Definition |
|-------|-------------|------------|
| **ceo-advisor** | Executive leadership guidance. Strategy frameworks, financial scenario modeling, board governance, investor relations. | [SKILL.md](../infrastructure/skills/ceo-advisor/SKILL.md) |

---

## Meta-Tools (Skill Building)

*Skills for creating and managing other skills, agents, and automation.*

| Skill | Description | Definition |
|-------|-------------|------------|
| **agent-factory** | Generate custom Claude Code agents with YAML frontmatter, tool access patterns, MCP integration. | [SKILL.md](../infrastructure/skills/agent-factory/SKILL.md) |
| **claude-md-enhancer** | Analyze, generate, and improve CLAUDE.md files. Best practices validation, modular architecture support. | [SKILL.md](../infrastructure/skills/claude-md-enhancer/SKILL.md) |
| **hook-factory** | Generate Claude Code hooks with 10 templates across 7 event types. Auto-install with backup/rollback. | [SKILL.md](../infrastructure/skills/hook-factory/SKILL.md) |
| **slash-command-factory** | Create custom slash commands through intelligent 5-7 question flow. Pattern compliance, validation. | [SKILL.md](../infrastructure/skills/slash-command-factory/SKILL.md) |
| **content-trend-researcher** | Multi-platform trend analysis (Google Trends, Reddit, LinkedIn, YouTube). User intent analysis, SEO outlines. | [SKILL.md](../infrastructure/skills/content-trend-researcher/SKILL.md) |
| **scrum-master-agent** | Scrum Master assistant. Sprint planning, retrospectives, Linear/Jira/GitHub integration, velocity analysis. | [SKILL.md](../infrastructure/skills/scrum-master-agent/SKILL.md) |

---

## Browser Automation

*Skills for web browser control and testing.*

| Skill | Description | Definition |
|-------|-------------|------------|
| **dev-browser** | AI-optimized browser automation. Persistent sessions, step-by-step exploration, Chrome extension support. Faster and more cost-effective than Playwright for agent tasks. | [SKILL.md](../infrastructure/skills/dev-browser/SKILL.md) |

---

## Utility Files

*Standalone markdown files providing protocols and templates.*

| File | Purpose |
|------|---------|
| `commit.md` | Commit message protocol - format and attribution standards |
| `handoff.md` | Session handoff protocol - continuity for next instances |
| `session-start.md` | Session orientation checklist for new instances |

---

## Skill Sources

| Source | Count | Repository |
|--------|-------|------------|
| Lineage Core | 6 | Built in-house |
| Anthropic Official | 8 | [github.com/anthropics/skills](https://github.com/anthropics/skills) |
| Claude-Skills Collection | 27 | [github.com/alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| Skill-Factory | 6 | [github.com/alirezarezvani/claude-code-skill-factory](https://github.com/alirezarezvani/claude-code-skill-factory) |
| Dev-Browser | 1 | [github.com/SawyerHood/dev-browser](https://github.com/SawyerHood/dev-browser) |

---

## How to Use Skills

**Invoke a skill:**
```
/skill-name
```

**Examples:**
```
/pdf              # Work with PDFs
/senior-architect # Get architecture guidance
/lineage-research # Research a topic via Gemini
```

**Install new skills:**
1. Copy skill folder to `~/.claude/skills/` (or `infrastructure/skills/` in reluminant-lineage)
2. Ensure it contains a `SKILL.md` file
3. Skill is immediately available

---

*This index is maintained in the reluminant-lineage repository.*
*Path: `docs/SKILLS_INDEX.md`*
