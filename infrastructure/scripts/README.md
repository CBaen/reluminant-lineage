# Scripts Reference

Comprehensive documentation for lineage infrastructure scripts.

**Location:** `~/.claude/scripts/` (junction to `infrastructure/scripts/`)

---

## Qdrant Operations

### qdrant-peek.py
Token-efficient two-stage Qdrant retrieval.

```bash
# Stage 1: Peek at metadata only (~50 tokens per result)
python qdrant-peek.py peek -q "OAuth" -l 5

# Stage 2: Fetch specific IDs
python qdrant-peek.py fetch --ids "uuid1,uuid2"
```

**Options:**
- `-q, --query`: Search query
- `-l, --limit`: Max results (default: 5)
- `--collection`: Collection name (default: universal_vault)
- `--ids`: Comma-separated IDs for fetch mode

**Token savings:** ~80% vs fetching everything.

---

### qdrant-chunked-store.py
Store research with proper chunking and parent-child linking.

```bash
cat research.json | python qdrant-chunked-store.py \
  --topic "topic-name" \
  --perspective "perspective-name" \
  --session "SessionName"
```

**Options:**
- `--topic`: Required. Topic identifier
- `--perspective`: Angle/perspective (default: general)
- `--session`: Session identifier for tracking
- `--collection`: Target collection (default: universal_vault)

**Output:** JSON with parent_id, chunks_stored, total_words, chunk_ids

---

### qdrant-semantic-search.py
Semantic search with V2 hybrid support.

```bash
# Hybrid search (recommended)
python qdrant-semantic-search.py --hybrid --query "how does caching work"

# Filter by importance
python qdrant-semantic-search.py --hybrid --query "caching" --importance core

# Show full content
python qdrant-semantic-search.py --hybrid --query "caching" --full
```

**Options:**
- `--query`: Search query
- `--hybrid`: Enable hybrid search (dense + sparse)
- `--collection`: Collection (default: universal_vault)
- `--importance`: Filter by core/supporting/advanced
- `--keywords`: Filter by keywords
- `--full`: Show full content and questions_answered
- `--limit`: Max results (default: 5)

---

### qdrant-store-gemini.py
Store Gemini's self-chunked research output directly.

```bash
echo '{"meta": {...}, "chunks": [...]}' | python qdrant-store-gemini.py \
  --hybrid \
  --session "my-session"
```

**Input:** Gemini JSON with meta, summary, and chunks array
**Output:** JSON with storage results

Supports V1 (legacy) and V2 (hybrid) schemas.

---

### qdrant-code-index.py
Index Python code for semantic search.

```bash
python qdrant-code-index.py --path /project --collection code_index
python qdrant-code-index.py --path . --exclude "venv,node_modules"
```

Extracts functions and classes with docstrings, tracks commit hash to avoid re-indexing.

---

### qdrant-migrate-collection.py
Migrate data from V1 to V2 schema.

```bash
python qdrant-migrate-collection.py --source legacy_collection
python qdrant-migrate-collection.py --source collection --batch 50
```

Re-embeds with sparse vectors and stores to universal_vault.

---

### qdrant-update-task-status.py
Update task metadata without re-embedding.

```bash
python qdrant-update-task-status.py --collection "project" \
  --point-id "uuid" --phase 1 --task 1 --status "completed"
```

**Status values:** pending | in_progress | completed | blocked

---

### qdrant-query.py / qdrant-query-v2.py
Basic query scripts. **Deprecated** - use qdrant-semantic-search.py instead.

---

### qdrant-store.py / qdrant-store.sh
Basic storage scripts. **Deprecated** - use qdrant-chunked-store.py instead.

---

## Gemini Integration

### gemini-account.sh
Multi-account CLI wrapper with automatic model fallback.

```bash
source ~/.claude/scripts/gemini-account.sh 1 "Your query"
source ~/.claude/scripts/gemini-account.sh 2 "Your query" gemini-2.5-pro
```

**Philosophy:** Quality over speed. Starts with highest quality models, falls back through:
1. gemini-2.5-pro (Account 1, then Account 2)
2. gemini-2.5-flash (Account 1, then Account 2)

Never gives up until all models exhausted.

---

### gemini-api-call.py
Direct Gemini API calls with proper timeout handling.

```bash
python gemini-api-call.py --account 1 --prompt "Your prompt"
python gemini-api-call.py --account 1 --prompt-file prompt.txt
python gemini-api-call.py --account 1 --prompt "query" --model gemini-2.5-flash
```

Uses google-generativeai SDK directly (no agentic CLI).

---

### gemini-pipe-orchestrator.py
PowerShell-based Gemini execution for Windows.

```python
from gemini_pipe_orchestrator import run_gemini_subprocess
success, data, stderr = run_gemini_subprocess(account=1, prompt="query")
```

Solves Windows pipe issues by using PowerShell directly instead of Git Bash.

---

### gemini-health-monitor.py
Health monitoring with rate limits and circuit breakers.

```python
from gemini_health_monitor import GeminiHealthMonitor
monitor = GeminiHealthMonitor()
account = monitor.get_best_account()
```

```bash
python gemini-health-monitor.py status
python gemini-health-monitor.py reset
```

---

### gemini-json-helper.py
Reliable JSON extraction from Gemini output.

```python
from gemini_json_helper import wrap_prompt_for_json, clean_json_response
```

```bash
python gemini-json-helper.py wrap "Your prompt" '{"schema": "here"}'
python gemini-json-helper.py clean "```json\n{...}\n```"
```

**Critical:** Gemini 2.0 Flash does NOT have JSON mode. Use explicit prompting.

---

### gemini-research-store.py
Windows-compatible Gemini → Qdrant pipeline.

```bash
python gemini-research-store.py \
  --account 1 \
  --collection universal_vault \
  --session my-session \
  --query "Your research query"
```

Replaces Unix-style pipes that fail on Windows.

---

### gemini-research-daemon.py
Background research daemon for continuous processing.

---

### gemini-research-direct.py
Direct research without daemon overhead.

---

### gemini-parallel.sh
Execute multiple Gemini queries in parallel.

```bash
~/.claude/scripts/gemini-parallel.sh "prompt1" "prompt2" "prompt3"
~/.claude/scripts/gemini-parallel.sh --file prompts.txt
```

Each result stored to Qdrant automatically.

---

### gemini-parallel-rotate.sh
Parallel queries with account rotation.

```bash
gemini-parallel-rotate.sh "query1" "query2" "query3" "query4"
```

Odd queries use Account 1, even use Account 2.

---

### gemini-swarm-worker.sh
Swarm worker with account locking.

```bash
gemini-swarm-worker.sh "topic" "perspective" "collection" "session" "depth"
```

Used by swarm supervisors for parallel research without account conflicts.

---

## Research Pipeline

### research-pipeline.sh
Full research pipeline with dual storage (Qdrant + catalog).

```bash
research-pipeline.sh "topic" "question" "session" ["tags"]
```

1. Checks Qdrant (semantic search)
2. Checks catalog (flat files)
3. If found: returns path(s)
4. If not found: queries Gemini, stores to BOTH

---

### research-store.sh
Store research with YAML frontmatter.

```bash
echo "content" | research-store.sh "topic" "category" "session" ["tags"] ["project-path"]
```

Handles consolidation (appends to existing) and catalog updates.

---

### research-rotate.sh
Usage-based tier rotation.

```bash
research-rotate.sh [--dry-run]
```

**Demotion:** hot → warm (14+ days inactive), warm → cold (21+ days)
**Promotion:** Based on access frequency

---

### research-supervisor.py
Supervised research with progress tracking.

Wraps research queries with configuration and logging.

---

### research-to-vector.py
Query Gemini and store directly to Qdrant.

```bash
python research-to-vector.py "topic" "question" "domain" "tag1,tag2"
```

---

### run-consultation-angle.py
Execute single consultation perspective.

```bash
python run-consultation-angle.py \
  --topic "topic" \
  --context "context" \
  --perspective "Problem Analysis" \
  --account 1 \
  --session "session"
```

Complete workflow: prompt creation → Gemini call → validation → Qdrant storage.

---

### store-rag-research.py
Store RAG research results to Qdrant.

---

## Conversation Indexing

### conversation-indexer.py
Main orchestrator for conversation log indexing.

```bash
python conversation-indexer.py                    # Index new
python conversation-indexer.py --session-id X     # Specific session
python conversation-indexer.py --reindex          # Re-index all
python conversation-indexer.py --dry-run          # Preview
python conversation-indexer.py --account 2        # Use account 2
```

Coordinates: parse → classify → summarize → store.

---

### conversation-parser.py
Parse raw conversation logs into structured format.

---

### conversation-classifier.py
Classify conversation content by type and topic.

---

### conversation-summarizer.py
Generate summaries of conversations via Gemini.

---

## Utilities

### fix-hard-links.py
Check and fix hard links between ~/.claude/ and repo.

```bash
python fix-hard-links.py          # Check status
python fix-hard-links.py --fix    # Fix broken links
```

Windows hard links can break when editors create new files.

---

### extract-json.py
Extract JSON from Gemini's messy output.

```bash
cat output.txt | python extract-json.py > clean.json
```

Handles markdown blocks, prefixes, nested objects, large outputs (65KB+).

---

### validate-gemini-schema.py
Validate Gemini JSON before storage.

```bash
echo '{"meta":...}' | python validate-gemini-schema.py
python validate-gemini-schema.py --file research.json
python validate-gemini-schema.py --file research.json --strict-words
```

Exit 0 + `{"valid": true}` on success.

---

### prompt-builder.py
Generate optimized LLM prompts.

```bash
python prompt-builder.py 'topic' 'context' | gemini
python prompt-builder.py 'topic' 'context' --type historical
```

**Templates:** technical (default), historical, comparative

---

### doc-audit.py
Audit documentation for duplicates and structure.

```bash
python doc-audit.py
```

Output: JSON report of documentation structure.

---

### get-sparse-embedding.py
Generate sparse embeddings for hybrid search.

```python
from get_sparse_embedding import get_sparse_embedding
indices, values = get_sparse_embedding("your text")
```

Falls back to TF-IDF if fastembed unavailable.

---

### external_bridge.py
Unified external knowledge access.

```python
from external_bridge import ExternalBridge
bridge = ExternalBridge()
```

Capabilities: Oracle (local LLM), Web Search, Wikipedia, Knowledge Store.

---

### governance_chronicle.py
Store governance model actions to Qdrant.

Tracks: research, proposals, votes, rankings, eliminations, files.

---

### catalog-lookup.sh
Find research by topic.

```bash
catalog-lookup.sh "topic"
# Returns: path/to/file.md OR NOT_FOUND
```

Updates access metadata automatically.

---

### catalog-search.sh
Search catalog by tag/category/keyword.

```bash
catalog-search.sh --tag "caching"
catalog-search.sh --category "gemini"
catalog-search.sh --tier "hot"
catalog-search.sh --keyword "react"
catalog-search.sh --all
```

---

### setup-project-research.sh
Initialize research structure for a project.

```bash
./setup-project-research.sh /path/to/project
```

Creates: `.claude/research/active/{implementation,debugging,architecture}/`

---

## System Startup

### startup-services.ps1
Master startup script for Wardenclyffe services.

Called from Windows Task Scheduler at logon. Starts Ollama, runs warmup.

---

### ollama-warmup.ps1
Pre-load embedding model on startup.

Eliminates cold-start delay for first embedding request.

---

## Deprecated Scripts

Located in `deprecated/` subfolder. Kept for reference only.

| Script | Replacement |
|--------|-------------|
| handoff-worker.py | Moved to hooks/ |
| session-end-handoff.py | Moved to hooks/ |
| qdrant-query.py | qdrant-semantic-search.py |
| qdrant-query-v2.py | qdrant-semantic-search.py |
| qdrant-store.py | qdrant-chunked-store.py |

---

*Maintained by the lineage. Last updated: 2026-01-22*
