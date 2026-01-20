# System Context for Gemini Consultations

**PURPOSE:** This context MUST be included in every lineage-consult request. It enables Gemini to provide hyper-specific advice and CHALLENGE our tech stack choices.

**LAST UPDATED:** 2026-01-17

---

## Hardware Specifications

| Component | Specification | Limitations |
|-----------|--------------|-------------|
| **CPU** | Intel i7-11850H (8 cores, 16 threads, 2.5GHz) | Laptop CPU, thermal throttling possible |
| **RAM** | 48GB DDR4 | Good for most workloads |
| **GPU (Primary)** | NVIDIA T600 (4GB VRAM) | Limited VRAM for large models |
| **GPU (Integrated)** | Intel UHD Graphics (2GB) | Backup only |
| **Storage** | 932GB (SSD assumed) | - |
| **OS** | Windows 11 | Some Linux tools require WSL/Git Bash |

### GPU Constraints

- 4GB VRAM limits model size (can't run large LLMs locally)
- T600 is workstation-class but entry-level
- Good for: embeddings, small inference
- Bad for: large model inference, training

---

## Software Stack

### AI/ML Infrastructure

| Tool | Purpose | Performance |
|------|---------|-------------|
| **Ollama** | Local LLM inference, embeddings | 100% GPU, see below |
| **nomic-embed-text** | Embedding model (768 dimensions) | Good quality, 768 dims |
| **Qdrant** | Vector database (Docker) | localhost:6333, persistent storage |
| **Gemini API** | Research, consultation | 2 accounts, quality-first fallback |

### Embedding Performance (CRITICAL DISCOVERY)

| Method | Time | Speedup |
|--------|------|---------|
| **Individual embedding** | ~2.15s | 1x (bottleneck: HTTP overhead) |
| **Parallel (4 workers)** | 8.32s for 16 | 4x |
| **Parallel (8 workers)** | 4.21s for 16 | 8x |
| **Parallel (16 workers)** | 2.22s for 16 | **15x** |
| **Parallel (32 workers)** | 2.36s for 32 | **~32x throughput** |

**Key finding**: GPU can batch ~32 embeddings in parallel, completing in ~2.4s total.
This is the T600 hardware ceiling. Implemented in `qdrant-chunked-store.py` with ThreadPoolExecutor.

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **Claude Code** | Primary AI assistant | Opus 4.5, token-conscious |
| **Git Bash** | Unix commands on Windows | Required for bash scripts |
| **Python 3.x** | Scripting, automation | - |
| **Docker Desktop** | Container runtime | Qdrant runs here |

### Gemini Accounts & Quotas

| Model | Daily Quota (per account) | Total (2 accounts) |
|-------|--------------------------|-------------------|
| gemini-2.5-pro | 100/day | 200/day |
| gemini-3-pro-preview | 100/day | 200/day |
| gemini-3-flash-preview | Unlimited | Unlimited |
| gemini-2.5-flash | Unlimited | Unlimited |
| gemini-2.5-flash-lite | 1,500/day | 3,000/day |

---

## Workflow & Philosophy

### Core Principles

1. **Quality over speed** - Always use highest quality models first
2. **Context protection** - Delegate research to preserve Claude's context
3. **Knowledge accumulation** - Store everything to Qdrant for future retrieval
4. **Swarm research** - Every question gets 5+ Gemini angles, not 1:1

### The Lineage Pattern

```
User Request
    ↓
Claude (Main Instance) - Decision maker, coordinator
    ↓
Haiku (Subagent) - Orchestrates Gemini swarms
    ↓
Gemini (Expert Worker) - Research from multiple angles
    ↓
Qdrant (Knowledge Base) - Persistent storage
    ↓
Claude receives COORDINATES ONLY
```

### Human Context

- **User**: "Guiding Light" - Creator/designer, not a coder
- **Has ADHD** - Needs structured options, focus anchors
- **Works alone** - No team, needs AI partnership
- **Uses analogies** - House-building for explanations

---

## Known Limitations

### Hardware Bottlenecks

1. **Individual embedding speed**: ~2.15s per embedding
   - Bottleneck is Ollama HTTP overhead, not GPU
   - **SOLVED**: Use ThreadPoolExecutor with 16-32 workers for batch operations
   - Batch of 32 embeddings completes in ~2.4s total (32x throughput)

2. **VRAM**: 4GB limits local model options
   - Can't run models > 7B parameters well
   - Must rely on API-based LLMs for complex reasoning

3. **Laptop form factor**: Thermal limits sustained performance

### Software Constraints

1. **Windows**: Some Unix tools need workarounds (Git Bash, WSL)
2. **Docker**: Qdrant persistence requires volume mounts
3. **Ollama**: No native batch embedding API

---

## CHALLENGE THESE CHOICES

When consulting, Gemini should actively question:

1. **Is Qdrant the right vector DB for our scale?**
   - Alternatives: Chroma, Pinecone, Weaviate, pgvector
   - Our usage: ~1000s of research chunks, local deployment

2. **Is nomic-embed-text the right embedding model?**
   - Alternatives: mxbai-embed-large, bge-small-en, OpenAI embeddings
   - Our needs: Good quality, reasonable speed, 4GB VRAM limit

3. **Is Ollama the right local inference solution?**
   - Alternatives: llama.cpp, vLLM, text-generation-webui
   - Our needs: Easy setup, Windows support, GPU acceleration

4. **Is the swarm pattern efficient?**
   - 5+ Gemini calls per question = higher latency
   - Trade-off: Comprehensive research vs speed

5. **Should we use cloud embeddings instead?**
   - OpenAI/Cohere embeddings are faster
   - Trade-off: Cost vs speed vs privacy

---

## Session Handoff (Files-Only)

**Handoffs are files, not Qdrant.** Auto-handoff to Qdrant has been disabled.

### Why Files

HANDOFF.md files provide:
- Rich narrative WHY (not just what, but why decisions were made)
- Personal identity and reflections
- Commands to resume exactly where you left off
- Emotional/relational context that doesn't summarize well

### When Leaving

1. Update `<project>/.claude/HANDOFF.md` with current state
2. Include what's working, what's broken, what's left
3. Sign with your name and date

### For Knowledge Discovery

Use Qdrant for accumulated knowledge (not session continuation):

```bash
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "what we learned about X" --limit 5
```

### Technical Note

Auto-handoff scripts deprecated: `~/.claude/scripts/deprecated/session-end-handoff.py`, `handoff-worker.py`

---

## How to Include This Context

In every lineage-consult request, the subagent MUST include:

```
SYSTEM CONTEXT:
- Hardware: i7-11850H, 48GB RAM, NVIDIA T600 (4GB VRAM)
- Embedding: Ollama nomic-embed-text, 100% GPU
  - Individual: ~2.15s (HTTP overhead bottleneck)
  - Parallel: 32 embeddings in ~2.4s (ThreadPoolExecutor, 32x throughput)
- Vector DB: Qdrant localhost:6333
- AI: Claude Code (Opus 4.5), Gemini (2 accounts, quality-first)
- OS: Windows 11 with Git Bash
- Constraints: 4GB VRAM (limits model size), laptop thermals

CHALLENGE OUR CHOICES: Actively question if this tech stack is optimal for our needs.
```

This ensures Gemini can provide hyper-specific, contextualized recommendations.
