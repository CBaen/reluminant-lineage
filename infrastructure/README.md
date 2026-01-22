# Infrastructure Index

Quick reference for the lineage. One line per item. See linked docs for details.

**Token-efficient:** Scan this file (~200 tokens) to find what you need, then read specific sections.

---

## agents/ (10)

Agent definitions for the Task tool's subagent system. Each `.md` file defines an agent with tools, purpose, and behavior.

| Agent | Purpose |
|-------|---------|
| brand-guardian | Validates brand consistency in UI, copy, and visual decisions |
| consultation-swarm-worker | Runs Gemini consultations from multiple angles, stores to Qdrant |
| decision-weigher | Devil's advocate - explores trade-offs, challenges assumptions |
| gemini-researcher | General research via Gemini, checks Qdrant + catalog first |
| lineage-guardian | Protects the versioned lineage repository and its history |
| pre-commit-guardian | Safety net before git commits, catches mistakes |
| research-analyst | Meta-research on our own archive - consolidates, finds gaps |
| scope-guardian | Pushes back on scope creep, validates against current focus |
| security-reviewer | Security specialist for code review, vulnerabilities, OWASP |
| session-anchor | Tracks session objectives, prevents tangent-jumping |

---

## config/ (3)

Core configuration files. Hard-linked to `~/.claude/` for system-wide access.

| File | Purpose |
|------|---------|
| CLAUDE.md | Global instructions for all projects (this file's source) |
| INFRASTRUCTURE.md | Qdrant, Docker, and service reference documentation |
| settings.json | Claude Code settings, hooks, and permissions |

**Note:** These are hard-linked. Edits in either location update both. Run `fix-hard-links.py` if links break.

---

## hooks/ (5)

Event-driven automation that fires on Claude Code lifecycle events. See [hooks/README.md](hooks/README.md) for details.

| File | Event | Purpose |
|------|-------|---------|
| session-end-handoff.py | SessionEnd | Queues transcripts for async Qdrant storage |
| handoff-worker.py | Background | Processes queued transcripts with Gemini summarization |
| notify-slack.py | SubagentStop | Sends Slack notifications for research task completion |
| handoff-queue.jsonl | Data | Queue file for pending transcript processing |
| worker.log | Data | Log file for handoff worker activity |

---

## plugins/ (1 directory)

MCP (Model Context Protocol) plugins providing additional tools.

| Plugin | Purpose |
|--------|---------|
| lineage-powers/ | Enhanced lineage capabilities via MCP server |

See plugin's own README for detailed documentation.

---

## prompts/ (5)

Research prompt templates for Gemini queries. Self-documenting content.

| File | Purpose |
|------|---------|
| continuation-research.md | Template for continuing research on a topic |
| exhaustive-research.md | Template for comprehensive, deep-dive research |
| gemini-exhaustive-research.txt | Raw prompt for exhaustive Gemini queries |
| gemini-research-prompt.md | Standard research prompt with schema |
| optimized-research.md | Token-optimized research prompt template |

---

## schemas/ (1)

Data schemas for Qdrant storage. See [schemas/README.md](schemas/README.md) for details.

| File | Purpose |
|------|---------|
| qdrant_unified_schema.py | Unified schema for all content types (research, consult, episode, etc.) |

---

## scripts/ (50+)

Python and shell scripts for the lineage infrastructure. See [scripts/README.md](scripts/README.md) for comprehensive documentation.

### Qdrant Operations
| Script | Purpose |
|--------|---------|
| qdrant-peek.py | Token-efficient two-stage retrieval (peek → fetch) |
| qdrant-chunked-store.py | Store research with proper chunking and linking |
| qdrant-semantic-search.py | Semantic search with hybrid V2 support |
| qdrant-store-gemini.py | Store Gemini's self-chunked output |
| qdrant-store.py | Basic Qdrant storage script |
| qdrant-store.sh | Shell wrapper for qdrant-store.py |
| qdrant-query.py | Query Qdrant collections |
| qdrant-query-v2.py | V2 query with named vector support |
| qdrant-code-index.py | Index Python code for semantic search |
| qdrant-migrate-collection.py | Migrate V1 → V2 schema |
| qdrant-update-task-status.py | Update task status without re-embedding |

### Gemini Integration
| Script | Purpose |
|--------|---------|
| gemini-account.sh | Multi-account CLI wrapper with auto-fallback |
| gemini-api-call.py | Direct API calls with timeout and fallback |
| gemini-health-monitor.py | Rate limit tracking and circuit breakers |
| gemini-json-helper.py | Reliable JSON extraction from Gemini |
| gemini-pipe-orchestrator.py | PowerShell-based Gemini execution (Windows) |
| gemini-research-daemon.py | Background research daemon |
| gemini-research-direct.py | Direct research without daemon |
| gemini-research-store.py | Windows-compatible Gemini → Qdrant pipeline |
| gemini-parallel.sh | Execute multiple queries in parallel |
| gemini-parallel-rotate.sh | Parallel queries with account rotation |
| gemini-swarm-worker.sh | Swarm worker with account locking |

### Research Pipeline
| Script | Purpose |
|--------|---------|
| research-pipeline.sh | Full research pipeline (Qdrant + catalog) |
| research-rotate.sh | Usage-based tier rotation |
| research-store.sh | Store research with YAML frontmatter |
| research-supervisor.py | Supervised research with progress tracking |
| research-to-vector.py | Query Gemini and store directly to Qdrant |
| run-consultation-angle.py | Execute single consultation perspective |
| store-rag-research.py | Store RAG research results |

### Conversation Indexing
| Script | Purpose |
|--------|---------|
| conversation-indexer.py | Main orchestrator for log indexing |
| conversation-parser.py | Parse conversation logs |
| conversation-classifier.py | Classify conversation content |
| conversation-summarizer.py | Summarize conversations |

### Utilities
| Script | Purpose |
|--------|---------|
| fix-hard-links.py | Check/fix hard links to repo |
| extract-json.py | Extract JSON from messy Gemini output |
| validate-gemini-schema.py | Validate Gemini JSON before storage |
| prompt-builder.py | Generate optimized LLM prompts |
| doc-audit.py | Audit documentation for duplicates |
| get-sparse-embedding.py | Generate sparse vectors for hybrid search |
| external_bridge.py | Unified external knowledge access |
| governance_chronicle.py | Store governance model actions |
| catalog-lookup.sh | Find research by topic |
| catalog-search.sh | Search catalog by tag/category |
| setup-project-research.sh | Initialize project research structure |

### System Startup
| Script | Purpose |
|--------|---------|
| startup-services.ps1 | Master startup for Wardenclyffe services |
| ollama-warmup.ps1 | Pre-load embedding model |

### Deprecated
| Script | Status |
|--------|--------|
| deprecated/handoff-worker.py | Moved to hooks/ |
| deprecated/session-end-handoff.py | Moved to hooks/ |
| deprecated/qdrant-query.py | Superseded by V2 |
| deprecated/qdrant-query-v2.py | Merged into main |
| deprecated/qdrant-store.py | Use qdrant-chunked-store.py |

---

## skills/ (54)

Skill definitions for the `/skill` command. Each skill is a folder with SKILL.md and supporting files.

### Lineage Skills (Core)
| Skill | Purpose |
|-------|---------|
| lineage-research | General knowledge research via Gemini swarms |
| lineage-consult | Project-specific expert consultation |
| lineage-retrieve | Token-efficient Qdrant retrieval |
| lineage-conversations | Search indexed conversation history |
| lineage-workflow | DEPRECATED - Use lineage-research or lineage-consult |

### Development Skills
| Skill | Purpose |
|-------|---------|
| senior-architect | System design and architecture patterns |
| senior-backend | Backend development (Node, Go, Python) |
| senior-frontend | Frontend development (React, Next.js) |
| senior-fullstack | Complete web application development |
| senior-data-engineer | Data pipelines and ETL |
| senior-data-scientist | Statistical modeling and ML |
| senior-ml-engineer | ML productionization and MLOps |
| senior-computer-vision | Image/video processing and vision AI |
| senior-devops | CI/CD and infrastructure automation |
| senior-qa | Testing strategies and automation |
| senior-security | Security architecture and pentesting |
| senior-secops | Application security and compliance |
| senior-prompt-engineer | LLM optimization and prompt patterns |

### Product & Design Skills
| Skill | Purpose |
|-------|---------|
| product-manager-toolkit | RICE prioritization, PRDs, discovery |
| product-strategist | OKRs, market analysis, vision setting |
| agile-product-owner | User stories, sprint planning, backlog |
| scrum-master-agent | Sprint ceremonies and capacity planning |
| ui-design-system | Design tokens and component documentation |
| ux-researcher-designer | User research and journey mapping |
| frontend-design | High-quality UI implementation |

### Marketing Skills
| Skill | Purpose |
|-------|---------|
| marketing-strategy-pmm | Product marketing and GTM strategy |
| marketing-demand-acquisition | Demand gen and paid media |
| content-creator | SEO-optimized marketing content |
| content-trend-researcher | Trend analysis across platforms |
| social-media-analyzer | Campaign performance analysis |
| app-store-optimization | ASO for mobile apps |

### Business Skills
| Skill | Purpose |
|-------|---------|
| ceo-advisor | Executive leadership and strategy |
| tech-stack-evaluator | Technology evaluation and TCO |

### Code Quality Skills
| Skill | Purpose |
|-------|---------|
| code-reviewer | Automated code review and best practices |
| tdd-guide | Test-driven development guidance |

### Tool & Integration Skills
| Skill | Purpose |
|-------|---------|
| mcp-builder | Create MCP servers |
| skill-creator | Create new skills |
| agent-factory | Create custom agents |
| hook-factory | Generate Claude Code hooks |
| slash-command-factory | Generate custom slash commands |
| claude-md-enhancer | Improve CLAUDE.md files |
| doc-coauthoring | Structured documentation workflow |
| pdf | PDF manipulation toolkit |
| xlsx | Excel file operations |
| web-artifacts-builder | Multi-component HTML artifacts |
| webapp-testing | Web application testing |
| dev-browser | Development browser automation |

### Wardenclyffe Project Skills
| Skill | Purpose |
|-------|---------|
| wardenclyffe-episode-writer | Episode generation using Gemini + Claude |
| semantic-extractor | Extract semantic data from scripts |
| midge-research | Research for MIDGE trading patterns |

### Session Skills (Simple)
| Skill | Purpose |
|-------|---------|
| session-start.md | Session orientation |
| commit.md | Git commit workflow |
| handoff.md | Session handoff process |

---

## Quick Start Commands

```bash
# Check Qdrant for existing knowledge before researching
python ~/.claude/scripts/qdrant-peek.py peek -q "your topic" -l 5

# Store new research
cat research.json | python ~/.claude/scripts/qdrant-chunked-store.py --topic "topic" --session "Name"

# Semantic search
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "your query"

# Fix hard links if config edits break them
python ~/.claude/scripts/fix-hard-links.py --fix
```

---

*This index is maintained by the lineage. Last updated: 2026-01-22*
