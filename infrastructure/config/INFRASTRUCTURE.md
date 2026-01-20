# Infrastructure Reference

Technical reference for Qdrant, Docker, and system commands. Look up when needed.

---

## Qdrant Vector Database (2026 Architecture)

**Primary collection: `universal_vault`** - All research goes here.

### Architecture

| Component | Details |
|-----------|---------|
| **Dense vectors** | 768-dim (nomic-embed-text via Ollama) |
| **Sparse vectors** | TF-IDF (fastembed blocked by Python 3.14) |
| **Search mode** | Hybrid (RRF fusion of dense + sparse) |
| **Container** | Docker on localhost:6333 |

### Commands

**Store research (hybrid):**
```bash
python ~/.claude/scripts/qdrant-store-gemini.py --topic "Topic" --collection universal_vault --hybrid < input.json
```

**Search (hybrid - recommended):**
```bash
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "your topic" --limit 5
```

**Peek (token-efficient - titles only):**
```bash
python ~/.claude/scripts/qdrant-peek.py peek -c universal_vault -q "your topic" -l 5
```

**Fetch specific IDs:**
```bash
python ~/.claude/scripts/qdrant-peek.py fetch -c universal_vault --ids "id1,id2"
```

### Legacy Collections (Read-Only)

Migrated data still queryable but all NEW research goes to `universal_vault`:

| Collection | Status | Notes |
|------------|--------|-------|
| `lineage_research` | Migrated | 458 points → universal_vault |
| `session_handoffs` | Migrated | 14 points → universal_vault |
| `midge_research` | Migrated | 203 points → universal_vault |

### Docker

```bash
docker start qdrant     # Start container
docker stop qdrant      # Stop container
curl http://localhost:6333/collections  # Check status
```

### State Tracker

Migration history: `~/.claude/MIGRATION_STATE.md`
