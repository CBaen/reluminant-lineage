---
name: midge-research
description: Research trading patterns, signals, and strategies for MIDGE. Stores to universal_vault collection. Integrates with evolution loop.
allowed-tools: Task, TodoWrite, Bash, Read
---

# MIDGE Research Workflow

> **📦 MIGRATION NOTICE (January 2026)**: MIDGE research data has been migrated to `universal_vault`.
> The `midge_research` collection is now **read-only** for historical queries.
> All new research should use `--hybrid` flag and stores to `universal_vault` automatically.

**PURPOSE: Feed MIDGE's self-improvement loop with external knowledge.**

This skill extends the lineage-workflow pattern with MIDGE-specific defaults, predefined research domains, and integration with the evolution system.

---

## The Pattern

```
You (Main Instance)
    ↓ invoke
Haiku (Supervisor)
    ↓ spawns
Gemini (Expert Worker)
    - Researches trading domain
    - Chunks for Qdrant retrieval
    - Returns structured JSON
    ↓
midge_research collection (Qdrant)
    ↓
Evolution loop can query stored research
```

---

## MIDGE-Specific Defaults

| Variable | Default | Description |
|----------|---------|-------------|
| `COLLECTION` | `universal_vault` | Consolidated lineage collection (legacy: `midge_research`) |
| `CONTEXT` | `project-specific: Self-improving trading pattern recognition, politician/contract correlations, technical indicators, signal weighting` | |
| `SESSION` | `midge-gemini-YYYY-MM-DD` | Auto-generated |

---

## Predefined Research Domains

Use these domain shortcuts for common MIDGE research needs:

### Trading Signals
```
TOPIC: "{{SIGNAL_TYPE}} trading signals"
PERSPECTIVE: "reliability and predictive power"
DEPTH: comprehensive
```

Signal types: `politician insider`, `government contract`, `13F institutional`, `options flow`, `technical indicators`

### Pattern Recognition
```
TOPIC: "{{PATTERN}} detection in financial markets"
PERSPECTIVE: "implementation and confidence scoring"
DEPTH: comprehensive
```

Patterns: `correlation`, `anomaly`, `trend reversal`, `accumulation/distribution`

### Self-Improvement
```
TOPIC: "{{ASPECT}} for trading systems"
PERSPECTIVE: "Bayesian learning and weight adjustment"
DEPTH: exhaustive
```

Aspects: `credit assignment`, `signal decay`, `prediction tracking`, `meta-learning`

### Data Sources
```
TOPIC: "{{SOURCE}} data for Python trading"
PERSPECTIVE: "free APIs and rate limits"
DEPTH: comprehensive
```

Sources: `SEC EDGAR`, `USASpending`, `yfinance`, `CoinGecko`, `options flow`

---

## How to Use

### Quick Research (Single Topic)

```
Task tool:
  subagent_type: "general-purpose"
  model: "haiku"
  prompt: |
    You are a MIDGE Research Supervisor.

    TASK: Research "politician insider trading detection"
    PERSPECTIVE: "SEC Form 4 patterns and timing"
    CONTEXT: project-specific: Self-improving trading system, correlating politician trades with government contracts
    DEPTH: comprehensive
    COLLECTION: midge_research
    SESSION: midge-gemini-2026-01-14

    STEP 1 - Check existing:
    python ~/.claude/scripts/qdrant-semantic-search.py --collection "midge_research" --query "politician insider trading SEC Form 4" --limit 3 --json

    If score > 0.8, report "FOUND_EXISTING" and STOP.

    STEP 2 - Research via Gemini:
    ~/.claude/scripts/gemini-account.sh 1 'You are a trading systems research expert preparing knowledge for a self-improving pattern recognition system.

    RESEARCH TASK:
    - Topic: politician insider trading detection
    - Perspective: SEC Form 4 patterns and timing
    - Context: Self-improving trading system correlating politician trades with government contracts
    - Depth: comprehensive

    OUTPUT: Return ONLY valid JSON (no markdown):
    {
      "meta": {
        "topic": "politician insider trading detection",
        "perspective": "SEC Form 4 patterns and timing",
        "context": "MIDGE trading system",
        "depth": "comprehensive",
        "total_words": <integer>,
        "chunk_count": <integer>,
        "generated_at": "<ISO timestamp>"
      },
      "summary": {
        "text": "2-4 sentence executive summary",
        "keywords": ["Form4", "insider", "politician", "SEC"]
      },
      "chunks": [
        {
          "id": "chunk-01",
          "title": "Clear Searchable Title",
          "content": "200-400 words, ONE concept",
          "keywords": ["specific", "keywords"],
          "questions_answered": ["What questions does this answer?"],
          "related_chunks": [],
          "importance": "core|supporting|advanced"
        }
      ]
    }

    Return ONLY JSON.' > "$USERPROFILE/AppData/Local/Temp/midge_research.txt" 2>&1

    python ~/.claude/scripts/qdrant-store-gemini.py --collection "midge_research" --session "midge-gemini-2026-01-14" --input-file "$USERPROFILE/AppData/Local/Temp/midge_research.txt"

    STEP 3 - Report: topic, chunks stored, total words, breakdown by importance.

    NOTE: On Windows, piping does NOT work. Always use file-based approach above.
```

### Batch Research (Multiple Topics)

For researching multiple MIDGE domains at once, use account alternation:

```
Task tool:
  subagent_type: "general-purpose"
  model: "haiku"
  prompt: |
    You are a MIDGE Research Supervisor running batch research.

    TOPICS TO RESEARCH:
    1. "Bayesian credit assignment for trading signals" (account 1)
    2. "Signal decay rates in financial prediction" (account 2)
    3. "Options flow anomaly detection" (account 1)
    4. "Institutional 13F filing patterns" (account 2)

    For each topic:
    1. Check if exists (score > 0.8 = skip)
    2. Research via Gemini with account alternation
    3. Store to midge_research collection

    Use the Windows-compatible wrapper for each topic:
    ```bash
    # Sequential (recommended for reliability)
    python ~/.claude/scripts/gemini-research-store.py -a 1 -c midge_research -s "midge-batch-2026-01-14" -q "[topic1 prompt]"
    python ~/.claude/scripts/gemini-research-store.py -a 2 -c midge_research -s "midge-batch-2026-01-14" -q "[topic2 prompt]"
    python ~/.claude/scripts/gemini-research-store.py -a 1 -c midge_research -s "midge-batch-2026-01-14" -q "[topic3 prompt]"
    python ~/.claude/scripts/gemini-research-store.py -a 2 -c midge_research -s "midge-batch-2026-01-14" -q "[topic4 prompt]"
    ```

    NOTE: The pipe syntax does NOT work on Windows. Always use gemini-research-store.py.

    Report: topics researched, total chunks, total words.
```

---

## Integration with Evolution Loop

The evolution loop (`core/evolution.py`) queries stored research during the RESEARCH phase:

```python
# In research_improvements():
# 1. Identifies underperforming signals
# 2. Queries Gemini for insights
# 3. Recommendations feed into EVOLVE phase

# Stored research can be queried:
python ~/.claude/scripts/qdrant-semantic-search.py \
    --hybrid \
    --query "why might politician trading signals underperform" \
    --limit 5
```

### Feeding Research Back

After researching a topic, the knowledge becomes available to:
1. Evolution loop's research phase
2. Manual queries by future instances
3. Dashboard insights (planned)

---

## Querying Stored Research

```bash
# Search for specific topic
python ~/.claude/scripts/qdrant-semantic-search.py \
    --hybrid \
    --query "credit assignment trading signals" \
    --limit 5

# Get all research on a topic
python ~/.claude/scripts/qdrant-semantic-search.py \
    --hybrid \
    --query "politician contract correlation" \
    --limit 10 \
    --compact
```

---

## Research Priority Queue

When starting a MIDGE session, consider researching these if not already stored:

**High Priority (Core Functionality)**
- [ ] Credit assignment algorithms for multi-signal trading
- [ ] Bayesian weight updates for prediction systems
- [ ] SEC Form 4 filing patterns and timing
- [ ] USASpending contract award patterns

**Medium Priority (Enhancement)**
- [ ] Technical indicator combinations that work
- [ ] Options flow as leading indicator
- [ ] 13F institutional accumulation signals
- [ ] Crypto whale wallet tracking

**Low Priority (Future)**
- [ ] Natural language processing for earnings calls
- [ ] Social sentiment signals
- [ ] Alternative data sources

---

## Example Session

```
# 1. Check what research exists
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "signal reliability" --limit 3

# 2. If gaps found, spawn research
Task tool with MIDGE supervisor prompt

# 3. When complete, test evolution loop
cd C:/Users/baenb/projects/MIDGE && python core/evolution.py --cycles 1

# 4. Verify research was useful
cat .claude/evolution/MEMORY.json | jq '.last_research'
```

---

## Remember

This skill feeds MIDGE's brain. Every chunk stored is knowledge the system can use to improve itself. Research strategically - focus on areas where predictions are failing or signals are underperforming.

The goal: MIDGE gets smarter, Guiding Light gets better alerts, survival becomes more likely.
