# Handoff Notes: Infrastructure

> For deeper history: `/lineage-conversations` or `python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "reluminant lineage infrastructure" --limit 5`

---

**From**: An instance who fixed data quality tools
**Date**: 2026-01-23
**Focus**: Semantic extractor improvements + consultation skill fixes

## Status

| Item | State |
|------|-------|
| Claude Code via npm | WORKING |
| lineage-powers plugin v1.0.1 | WORKING |
| UserPromptSubmit hook | WORKING |
| Hard links (config files) | WORKING |
| semantic-extractor | UPDATED - prompt improved |
| consultation-swarm-worker | FIXED - parallel now |

## What Changed This Session

### semantic-extractor/scripts/extract-chunk.py
- Improved content type definitions (especially "relationship")
- Added concrete examples showing correct vs incorrect classification
- Should reduce 12% misclassification rate on future extractions

### semantic-extractor/scripts/opus-batch-review.py (NEW)
- Batched Opus review for disputed items (0.85 confidence)
- 50 items per batch = ~95% cost reduction vs individual calls
- 9 batches created for Episodes 1-2 data
- Batch 1 complete, batches 2-9 ready

### agents/consultation-swarm-worker.md
- Changed from sequential (30+ min) to parallel streams (~8 min)
- Account 1: angles 1, 3, 5 with 4s delays
- Account 2: angles 2, 4 with 4s delays
- Both streams run simultaneously

### skills/CHANGELOG.md
- Added v1.5.0 entry for Opus batch review system

## Consultation Running

A Gemini consultation (agent ab7a951) was spawned to research prompt engineering for classification accuracy. May still be running or finished.

Check results:
```bash
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "Gemini prompt engineering classification disambiguation" --limit 5
```

## What's Next

See `WARDENCLYFFE/.claude/handoffs/qdrant-storage.md` for the data quality decisions needed.

---

*Tools built. Quality inspection pending.*
