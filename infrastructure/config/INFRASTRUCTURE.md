# Infrastructure Reference

Technical reference for hardware, Qdrant, Docker, and system commands. Look up when needed.

**Last updated:** 2026-01-22

---

## Hardware & GPU Policy

### System Specs

| Component | Specification |
|-----------|---------------|
| **CPU** | i7-11850H |
| **RAM** | 48GB |
| **Storage** | 932GB |
| **GPU** | Multi-GPU (4GB VRAM) |

### MANDATORY: Maximize GPU Usage

**Any process that CAN use the GPU MUST use it to the fullest extent.**

This has been a recurring problem - processes defaulting to CPU when GPU is available. When configuring or writing code that involves:

- **Ollama**: Ensure models are GPU-accelerated (`ollama ps` shows GPU layers)
- **Image generation**: Use Forge/A1111 with CUDA, enable RAM offloading for SDXL
- **Embeddings**: Ollama uses GPU by default, verify with `nvidia-smi`
- **LLM inference**: Always GPU-first, CPU fallback only if GPU OOM

### Verification Commands

```bash
# Check GPU usage
nvidia-smi

# Check Ollama GPU layers
ollama ps

# Monitor GPU during operations
nvidia-smi -l 1
```

### RAM Offloading (for 4GB VRAM)

When VRAM is insufficient:
- Enable RAM offloading (Forge supports this)
- SDXL: ~90 sec/image with offloading
- SD1.5: ~20 sec/image native

**Do NOT** fall back to CPU-only when offloading is available.

---

## Qdrant Vector Database

### Standard Workflow (MANDATORY)

**PEEK FIRST. Always.**

```bash
# 1. PEEK - Check what exists (~50 tokens per result)
python ~/.claude/scripts/qdrant-peek.py peek -q "your topic" -l 5

# 2. FETCH - Get full content for relevant IDs
python ~/.claude/scripts/qdrant-peek.py fetch --ids "id1,id2"

# 3. SEARCH - Full hybrid search if needed
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "your topic" --limit 5

# 4. STORE - After completing new research
cat research.json | python ~/.claude/scripts/qdrant-chunked-store.py \
  --topic "topic-name" \
  --perspective "research-angle" \
  --session "YourSessionName" \
  --collection "lineage_research" \
  --categories "tag1,tag2"
```

**Decision guide:**
| Score | Action |
|-------|--------|
| > 0.8 | Use existing - don't research |
| 0.5-0.8 | Read existing, may supplement |
| < 0.5 | Spawn new research |

---

### Architecture

| Component | Details |
|-----------|---------|
| **Dense vectors** | 768-dim (nomic-embed-text via Ollama) |
| **Sparse vectors** | BM25-style keyword matching |
| **Search mode** | Hybrid (RRF fusion of dense + sparse) |
| **Container** | `qdrant` on localhost:6333 |
| **Primary storage** | `universal_vault` (hybrid) or `lineage_research` (semantic) |

---

### Active Collections (as of 2026-01-20)

| Collection | Points | Purpose |
|------------|--------|---------|
| `universal_vault` | 2,583 | Primary hybrid storage |
| `locally_twisted_uiux` | 727 | Locally Twisted project |
| `emergence_self_knowledge` | 583 | Emergence project |
| `lineage_research` | 547 | General research archive |
| `ultrathink_analytics` | 317 | Ultrathink analytics |
| `locally_twisted_consult` | 206 | Project consultations |
| `midge_research` | 203 | MIDGE trading research |
| `code_test` | 155 | Code indexing |
| `trading_research` | 145 | Trading research |
| `tesla_mandela_effects` | 26 | WARDENCLYFFE podcast |
| `session_handoffs` | 14 | Session continuity |

---

### Storage Scripts

**Chunked storage (recommended for research):**
```bash
cat content.json | python ~/.claude/scripts/qdrant-chunked-store.py \
  --topic "topic" --perspective "angle" --session "Name" \
  --collection "lineage_research" --categories "tags"
```

**Gemini output storage:**
```bash
python ~/.claude/scripts/qdrant-store-gemini.py \
  --input-file response.json --hybrid --session "Name"
```

**Direct storage (simple content):**
```bash
echo "content" | python ~/.claude/scripts/qdrant-store-v2.py "topic" "collection" "session"
```

---

### Docker

```bash
docker start qdrant     # Start container
docker stop qdrant      # Stop container
docker ps               # Check running containers
curl http://localhost:6333/collections  # List collections
```

**Note:** Only ONE Qdrant container should exist, named `qdrant`. Delete any others.
