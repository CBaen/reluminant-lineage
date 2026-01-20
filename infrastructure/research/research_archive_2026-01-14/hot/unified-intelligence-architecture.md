# Wardenclyffe Intelligence Analysis System
## Unified Architecture v1.0

**Synthesized from**: 7 research documents totaling ~100K characters
**Date**: 2026-01-13
**Session**: Meta-Research Synthesis

---

## Overview

An autonomous intelligence analysis system for tracking global politics, financial institutions, power elite, social sentiment, environmental events, and commerce - with the goal of discovering hidden patterns between world events and financial movements.

**Constraints**: Solo operator + Claude + Gemini, local Qdrant, no massive infrastructure, incrementally buildable.

---

## Core Architecture

### Qdrant Collections

```
┌─────────────────────────────────────────────────────────────────┐
│                         QDRANT INSTANCE                          │
│                       localhost:6333                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  documents   │  │   entities   │  │   patterns   │           │
│  │              │  │              │  │              │           │
│  │ Raw data     │←→│ People, orgs │→→│ Cross-domain │           │
│  │ from sources │  │ events, locs │  │ correlations │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│         ↓                  ↓                  ↓                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              intelligence_events                     │        │
│  │                                                      │        │
│  │  Weighted events with:                              │        │
│  │  - Impact scores (0-100 logarithmic)                │        │
│  │  - Market correlations                               │        │
│  │  - Money flow signals                                │        │
│  │  - Granger causality tests                           │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why Qdrant-Only (No Neo4j)

Decision from A1 research: Graph databases add infrastructure overhead, ETL complexity, and cognitive load (two query languages). For our use case, Qdrant alone can simulate 1st and 2nd-degree connections through:

1. **Deterministic entity IDs**: `{entity_type}-{slugify(name)}`
2. **Two-way references**: Documents store `linked_entity_ids`, entities store `document_mentions`
3. **Co-occurrence = relationship**: Entities mentioned in same document are implicitly connected

---

## Schema Definitions

### Document Payload
```json
{
  "doc_id": "doc-a1b2c3d4",
  "source_name": "Reuters World News",
  "source_type": "news_article",
  "domain": "global_politics",
  "published_timestamp_utc": "2026-01-12T14:30:00Z",
  "linked_entity_ids": {
    "people": ["person-jane-doe"],
    "organizations": ["org-imf", "org-kremlin"],
    "locations": ["loc-moscow"],
    "events": ["event-sanctions-2026"]
  },
  "content": "...",
  "summary": "...",
  "tags": ["sanctions", "russia", "finance"]
}
```

### Entity Payload
```json
{
  "entity_id": "org-imf",
  "entity_type": "organization",
  "canonical_name": "International Monetary Fund",
  "aliases": ["IMF"],
  "summary": "International financial institution...",
  "document_mentions": ["doc-a1b2c3d4", "doc-e5f6g7h8"],
  "document_count": 2,
  "domain_appearances": ["finance", "politics"],
  "last_seen": "2026-01-12T14:30:00Z"
}
```

### Intelligence Event Payload
```json
{
  "event_id": "uuid",
  "domain": "political|financial|elite_networks|social_sentiment|environmental|commerce",
  "timestamps": {
    "event_time": "datetime",
    "detection_time": "datetime",
    "market_response_start": "datetime",
    "market_response_peak": "datetime",
    "lag_hours": "float"
  },
  "impact_scores": {
    "raw_impact": "float",
    "normalized_impact": "float[0-100]",
    "composite_impact": "float[0-100]",
    "confidence": "float[0-1]"
  },
  "market_effects": {
    "sp500_move_pct": "float",
    "btc_move_pct": "float",
    "affected_sectors": ["string"],
    "sector_moves": {"sector": "float"}
  },
  "money_flow": {
    "institutional_score": "float[-100,100]",
    "crypto_flow_score": "float[-100,100]",
    "dark_pool_ratio": "float[0,1]"
  },
  "correlations": {
    "granger_causality_pvalue": "float",
    "causal_direction": "cause|effect|bidirectional|unknown"
  }
}
```

### Pattern Payload
```json
{
  "pattern_id": "uuid",
  "pattern_signature": "political_tension → market_drop → elite_exit",
  "domains_involved": ["political", "financial", "elite_networks"],
  "temporal_sequence": [
    {"domain": "political", "lag_hours": 0},
    {"domain": "financial", "lag_hours": 4},
    {"domain": "elite_networks", "lag_hours": 24}
  ],
  "validation_state": "validated|hypothesis|deprecated",
  "confidence_score": 0.78,
  "replication_count": 12,
  "false_positive_rate": 0.15,
  "granger_causality_chain": [
    {"cause": "political", "effect": "financial", "pvalue": 0.003},
    {"cause": "financial", "effect": "elite_networks", "pvalue": 0.012}
  ]
}
```

---

## Impact Scoring System

### Logarithmic 0-100 Scale

```python
Impact Score = 100 * (1 - e^(-k * raw_impact))
```

### Domain Sensitivity Constants (k)

| Domain | k | Rationale |
|--------|---|-----------|
| Political | 0.15 | Slower, distributed impact |
| Financial | 0.35 | Direct, immediate effects |
| Elite Networks | 0.20 | Insider signal propagation delay |
| Social Sentiment | 0.25 | Viral spread dynamics |
| Environmental | 0.18 | Supply chain lag effects |
| Commerce | 0.30 | Direct economic measurement |

### Calibration Anchors

| Domain | Score 50 | Score 70 | Score 85 |
|--------|----------|----------|----------|
| Political | US Federal election | Brexit surprise | Regime change |
| Financial | 25bps rate change | 10% market correction | Lehman collapse |
| Elite | Sector-wide insider cluster | Buffett position change | Soros currency bet |
| Social | Coordinated campaigns | GameStop/WSB | Pandemic panic |
| Environmental | Category 3+ hurricane | Suez blockage | Multi-region crop failure |

---

## Intelligence Analysis Framework (ACH)

From B1 research - Analysis of Competing Hypotheses:

### AI Codification Steps

1. **Hypothesis Generation**: Given intelligence question, LLM generates mutually exclusive hypotheses
2. **Evidence Matrix**: Hypotheses as columns, evidence as rows
3. **Directed Search**: Queries for confirming AND disconfirming evidence
4. **Scoring**: Each evidence scored (-1 inconsistent, 0 neutral, +1 consistent)
5. **Ranking**: Hypothesis with highest consistency wins; confidence = score delta between top 2

### Red Flags for False Narratives

- **Circular Reporting**: Sources citing each other without primary
- **Source Monoculture**: Single ideological viewpoint
- **Perfect Fit**: Suspiciously clean evidence (possible disinfo)

---

## Entity Linking Strategy

From A2 research:

### Extraction Timing
Post-processing pass (not inline with research generation):
- Decouples creative research from structured extraction
- Allows reprocessing if schema changes
- Enables batch processing and parallelization

### Entity Types for Power Mapping

1. **Person**: Politicians, executives, donors, board members
2. **Organization**: Companies, NGOs, lobbying firms, think tanks
3. **Event**: Mergers, appointments, policy changes, meetings
4. **Location**: Cities, countries, regions
5. **Document**: Legislation, contracts, filings
6. **Concept**: Policies, movements, ideologies

### Entity Resolution via Gemini

```python
RESOLUTION_PROMPT = """
Given two entity mentions, determine if they refer to the same entity.

Entity A: {entity_a}
Context A: {context_a}

Entity B: {entity_b}
Context B: {context_b}

Are these the same entity? Respond with:
{
  "same_entity": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "..."
}
"""
```

---

## Connection Importance Tiers

From B2 research - Elite Network Analysis:

### Tier 1: Financial Flows (Highest Signal)
- Direct campaign contributions and bundling
- Corporate board compensation and stock grants
- Investment partnerships and carried interest
- Foundation grant relationships

### Tier 2: Structural Positions
- Board interlocks (companies sharing directors)
- Executive committee memberships
- Advisory board positions
- University trustee overlaps

### Tier 3: Social/Informal
- Club memberships (CFR, Bohemian Grove, Augusta)
- Educational institution ties (prep schools, Ivy League)
- Family connections and marriages

### Tier 4: Influence Infrastructure
- Think tank funding and advisory roles
- Media ownership and board seats
- Lobbying firm client overlaps

---

## Time-Decay and Freshness

From B3 research:

### Bi-Temporal Modeling

Every fact has two timestamps:
1. **Valid Time**: When the fact was true in the real world
2. **Transaction Time**: When the fact was recorded in the system

### Decay Functions by Knowledge Type

| Knowledge Type | Half-Life | Decay Model |
|---------------|-----------|-------------|
| Social sentiment | 24-72 hours | Exponential |
| News events | 1-7 days | Exponential |
| Financial positions | 45 days | Step (quarterly) |
| Elite relationships | 1-5 years | Linear |
| Corporate structure | 5-10 years | Very slow linear |

### Freshness Score Formula

```python
freshness = base_score * e^(-λ * days_since_event)

# Where λ = ln(2) / half_life_days
```

---

## Pattern Detection Algorithms

### Lead-Lag Detection

```python
def detect_lead_lag(series_a, series_b, max_lag=10):
    correlations = []
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            corr = np.corrcoef(series_a[:lag], series_b[-lag:])[0,1]
        elif lag > 0:
            corr = np.corrcoef(series_a[lag:], series_b[:-lag])[0,1]
        else:
            corr = np.corrcoef(series_a, series_b)[0,1]
        correlations.append((lag, corr))
    return max(correlations, key=lambda x: abs(x[1]))
```

### Granger Causality

```python
from statsmodels.tsa.stattools import grangercausalitytests

def test_causality(cause_series, effect_series, max_lag=5):
    data = np.column_stack([effect_series, cause_series])
    results = grangercausalitytests(data, maxlag=max_lag, verbose=False)
    best_lag = min(results.keys(), key=lambda k: results[k][0]['ssr_ftest'][1])
    return results[best_lag][0]['ssr_ftest'][1] < 0.05
```

### Delayed Effect Windows

| Window | Time Range | Weight |
|--------|------------|--------|
| Immediate | 0-4 hours | 0.35 |
| Same-day | 4-24 hours | 0.25 |
| Short-term | 1-7 days | 0.20 |
| Medium-term | 7-30 days | 0.15 |
| Long-term | 30-90 days | 0.05 |

---

## Money Flow Signals

### Institutional Signals

| Signal | Weight | Lag | Threshold |
|--------|--------|-----|-----------|
| 13F filings | 0.25 | 45 days | 10% position change |
| Dark pool activity | 0.30 | Real-time | >40% of volume |
| Options flow | 0.25 | Real-time | 3x normal value |
| ETF flows | 0.20 | 1 day | 2% of AUM |

### Crypto Signals

| Signal | Weight | Interpretation |
|--------|--------|----------------|
| Whale wallet movements | 0.35 | Exchange deposits = sell pressure |
| Exchange netflow | 0.30 | Positive = sell, Negative = accumulation |
| Stablecoin supply | 0.20 | >1.02 ratio = dry powder |
| Funding rates | 0.15 | >0.01 = overleveraged longs |

---

## Data Sources

### Political Analysis
- Government registries (UK Companies House, US IRS 990s)
- Legislative records (Congress.gov, UK Hansard)
- Election commission databases (US FEC)
- Court records (PACER, BAILII)

### Financial Tracking
- SEC EDGAR database
- OpenCorporates API
- ICIJ Offshore Leaks Database
- Shipping/aircraft tracking (ADS-B)
- Sanctions lists (OFAC, UN, EU)

### Elite Networks
- LittleSis.org (existing power mapping)
- BoardEx (executive relationships)
- Conference speaker lists (WEF, Davos)
- LinkedIn (professional connections)

### Social Trends
- Google Trends API
- Reddit API
- GDELT (news sentiment)
- Academic preprints

---

## Implementation Phases

### Phase 1: Core Schema
- [ ] Create Qdrant collections with schemas above
- [ ] Implement event ingestion pipeline
- [ ] Set up timestamp normalization

### Phase 2: Entity System
- [ ] Build entity extraction prompts for Gemini
- [ ] Implement entity resolution
- [ ] Create entity linker script

### Phase 3: Scoring System
- [ ] Implement domain-specific normalizers
- [ ] Calibrate baseline events from historical data
- [ ] Build composite impact calculator

### Phase 4: Pattern Detection
- [ ] Implement lead-lag detector
- [ ] Build Granger causality tester
- [ ] Create delayed effect analyzer

### Phase 5: Autonomous Operation
- [ ] Build priority queue for investigation
- [ ] Implement "watchable script" orchestrator
- [ ] Create alert system for threshold breaches

---

## Querying the Research

All source research is stored in the `system_architecture_research` collection:

```bash
# List all research documents
python3 ~/.claude/scripts/qdrant-query.py --collection system_architecture_research --list-all

# Query specific topic
python3 ~/.claude/scripts/qdrant-query-v2.py --collection system_architecture_research --topic "architecture-weights-measures-system" --content-only

# Search by tags
python3 ~/.claude/scripts/qdrant-query-v2.py --collection system_architecture_research --tags "qdrant,schema" --summary-only
```

---

*Architecture synthesized from lineage meta-research*
*2026-01-13*
