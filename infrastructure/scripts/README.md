# Scripts

Index of all scripts. Click name for full documentation.

**Location:** `~/.claude/scripts/` (junction to `infrastructure/scripts/`)

---

## Qdrant Operations

| Script | Purpose |
|--------|---------|
| [qdrant-peek.py](docs/qdrant-peek.md) | Token-efficient two-stage retrieval (peek → fetch) |
| [qdrant-chunked-store.py](docs/qdrant-chunked-store.md) | Store research with proper chunking and linking |
| [qdrant-semantic-search.py](docs/qdrant-semantic-search.md) | Semantic search with hybrid V2 support |
| [qdrant-store-gemini.py](docs/qdrant-store-gemini.md) | Store Gemini's self-chunked output |
| [qdrant-code-index.py](docs/qdrant-code-index.md) | Index Python code for semantic search |
| [qdrant-migrate-collection.py](docs/qdrant-migrate-collection.md) | Migrate V1 → V2 schema |
| [qdrant-update-task-status.py](docs/qdrant-update-task-status.md) | Update task status without re-embedding |
| [qdrant-query.py](docs/qdrant-query.md) | DEPRECATED - use qdrant-semantic-search.py |
| [qdrant-query-v2.py](docs/qdrant-query-v2.md) | DEPRECATED - use qdrant-semantic-search.py |
| [qdrant-store.py](docs/qdrant-store.md) | DEPRECATED - use qdrant-chunked-store.py |
| [qdrant-store.sh](docs/qdrant-store-sh.md) | DEPRECATED - use qdrant-chunked-store.py |

---

## Gemini Integration

| Script | Purpose |
|--------|---------|
| [gemini-account.sh](docs/gemini-account.md) | Multi-account CLI wrapper with auto-fallback |
| [gemini-api-call.py](docs/gemini-api-call.md) | Direct API calls with timeout and fallback |
| [gemini-pipe-orchestrator.py](docs/gemini-pipe-orchestrator.md) | PowerShell-based Gemini execution (Windows) |
| [gemini-health-monitor.py](docs/gemini-health-monitor.md) | Rate limit tracking and circuit breakers |
| [gemini-json-helper.py](docs/gemini-json-helper.md) | Reliable JSON extraction from Gemini |
| [gemini-research-store.py](docs/gemini-research-store.md) | Windows-compatible Gemini → Qdrant pipeline |
| [gemini-research-daemon.py](docs/gemini-research-daemon.md) | Background research daemon |
| [gemini-research-direct.py](docs/gemini-research-direct.md) | Direct research without daemon |
| [gemini-parallel.sh](docs/gemini-parallel.md) | Execute multiple queries in parallel |
| [gemini-parallel-rotate.sh](docs/gemini-parallel-rotate.md) | Parallel queries with account rotation |
| [gemini-swarm-worker.sh](docs/gemini-swarm-worker.md) | Swarm worker with account locking |

---

## Research Pipeline

| Script | Purpose |
|--------|---------|
| [research-pipeline.sh](docs/research-pipeline.md) | Full pipeline (Qdrant + catalog) |
| [research-store.sh](docs/research-store.md) | Store with YAML frontmatter |
| [research-rotate.sh](docs/research-rotate.md) | Usage-based tier rotation |
| [research-supervisor.py](docs/research-supervisor.md) | Supervised research with progress |
| [research-to-vector.py](docs/research-to-vector.md) | Query Gemini and store to Qdrant |
| [run-consultation-angle.py](docs/run-consultation-angle.md) | Execute single consultation perspective |
| [store-rag-research.py](docs/store-rag-research.md) | Store RAG research results |

---

## Conversation Indexing

| Script | Purpose |
|--------|---------|
| [conversation-indexer.py](docs/conversation-indexer.md) | Main orchestrator for log indexing |
| [conversation-parser.py](docs/conversation-parser.md) | Parse conversation logs |
| [conversation-classifier.py](docs/conversation-classifier.md) | Classify conversation content |
| [conversation-summarizer.py](docs/conversation-summarizer.md) | Summarize conversations |

---

## Utilities

| Script | Purpose |
|--------|---------|
| [fix-hard-links.py](docs/fix-hard-links.md) | Check/fix hard links to repo |
| [extract-json.py](docs/extract-json.md) | Extract JSON from messy Gemini output |
| [validate-gemini-schema.py](docs/validate-gemini-schema.md) | Validate Gemini JSON before storage |
| [prompt-builder.py](docs/prompt-builder.md) | Generate optimized LLM prompts |
| [doc-audit.py](docs/doc-audit.md) | Audit documentation for duplicates |
| [get-sparse-embedding.py](docs/get-sparse-embedding.md) | Generate sparse vectors for hybrid search |
| [external_bridge.py](docs/external-bridge.md) | Unified external knowledge access |
| [governance_chronicle.py](docs/governance-chronicle.md) | Store governance model actions |
| [catalog-lookup.sh](docs/catalog-lookup.md) | Find research by topic |
| [catalog-search.sh](docs/catalog-search.md) | Search catalog by tag/category |
| [setup-project-research.sh](docs/setup-project-research.md) | Initialize project research structure |
| [test-consultation-workflow.py](docs/test-consultation-workflow.md) | Test consultation workflow |

---

## System Startup

| Script | Purpose |
|--------|---------|
| [startup-services.ps1](docs/startup-services.md) | Master startup for Wardenclyffe services |
| [ollama-warmup.ps1](docs/ollama-warmup.md) | Pre-load embedding model |

---

*Index maintained by the lineage. Last updated: 2026-01-22*
