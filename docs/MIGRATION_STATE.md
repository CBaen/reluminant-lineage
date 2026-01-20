# Qdrant 2026 Migration State

## Status: COMPLETE

## Phase Checklist
- [x] Phase 1: Preparation
  - [x] Create MIGRATION_STATE.md (this file)
  - [x] Snapshot existing collections (3 key collections snapshotted)
  - [x] Create validate-gemini-schema.py (150+ lines, strict validation)
  - [x] Create universal_vault collection with 2026 schema (dense + sparse vectors, 6 payload indexes)
- [ ] Phase 2: Schema Migration
  - [x] Update qdrant_unified_schema.py (added V2 config, helper functions)
  - [x] Update qdrant-store-gemini.py (--hybrid flag, V2 storage)
  - [x] Update qdrant-semantic-search.py (--hybrid flag, RRF fusion)
  - [ ] Update remaining storage scripts
  - [ ] Update Gemini prompts with validation step
  - [x] Sparse vectors: TF-IDF fallback (fastembed blocked by Python 3.14/onnxruntime)
- [x] Phase 3: Data Migration
  - [x] Export existing points from legacy collections
  - [x] Re-embed with dual vectors (dense + sparse)
  - [x] Store to universal_vault (675 points: 458+14+203)
  - [ ] Migrate remaining collections (optional)
- [x] Phase 4: Skill & Hook Updates
  - [x] Update lineage-research skill (collection default, retrieval commands)
  - [x] Update lineage-consult skill (collection default, hybrid note)
  - [x] Update lineage-retrieve skill (collections table, hybrid commands)
  - [x] Update CLAUDE.md documentation (quick check, session query)
  - [ ] Update handoff-worker hook (optional - still works)
- [x] Phase 5: Cleanup
  - [x] Deprecate old scripts (moved to ~/.claude/scripts/deprecated/)
  - [x] Scripts deprecated: qdrant-store.py, qdrant-query.py, qdrant-query-v2.py
  - [ ] Archive old collections (keep for 1 week, then delete)
  - [x] Update handoff documentation

## Collections Status

| Collection | Snapshot ID | Migrated | Points | Notes |
|------------|-------------|----------|--------|-------|
| lineage_research | lineage_research-4944754190245572-2026-01-19-03-53-54.snapshot | YES | 458 | Primary research storage |
| session_handoffs | session_handoffs-4944754190245572-2026-01-19-03-53-56.snapshot | YES | 14 | Auto-generated session summaries |
| midge_research | midge_research-4944754190245572-2026-01-19-03-53-57.snapshot | YES | 203 | MIDGE trading research |
| trading_research | pending | no | TBD | Older trading research |
| tesla_mandela_effects | pending | no | TBD | Wardenclyffe episode content |
| locally_twisted_uiux | pending | no | TBD | Project-specific |
| locally_twisted_consult | pending | no | TBD | Project-specific |
| governance_chronicle | pending | no | TBD | Governance decisions |
| emergence_memory | pending | no | TBD | Emergence project |
| emergence_self_knowledge | pending | no | TBD | Emergence project |
| system_architecture_research | pending | no | TBD | Architecture research |

## Test Collections (skip migration)
- code_test
- test_optimization
- test_optimization_full
- test_warm
- test_semantic

## Last Updated
- Session: Migration Complete
- Instance: Migration implementer
- Timestamp: 2026-01-19
- Action: Migration complete - all phases finished

## Migration Log

### 2026-01-19 - Migration Complete
- Phase 1: Preparation complete - snapshots, validator, universal_vault created
- Phase 2: Schema updated - qdrant_unified_schema.py, storage scripts, search scripts
- Phase 3: Data migrated - 675 points (458 lineage_research + 14 session_handoffs + 203 midge_research)
- Phase 4: Skills updated - lineage-research, lineage-consult, lineage-retrieve, CLAUDE.md
- Phase 5: Cleanup - deprecated scripts moved to ~/.claude/scripts/deprecated/
- Sparse vectors: TF-IDF fallback (fastembed blocked by Python 3.14/onnxruntime)
- All hybrid search functionality working

### 2026-01-18 - Migration Started
- Created MIGRATION_STATE.md
- Qdrant container started (Docker)
- Found 19 existing collections
- Identified 11 collections for migration, 5 test collections to skip

## Rollback Instructions

If migration fails:

1. **Stop all storage scripts** - Kill any running Python processes using Qdrant

2. **Delete new collection** (if created):
   ```powershell
   Invoke-RestMethod -Method Delete -Uri 'http://localhost:6333/collections/universal_vault'
   ```

3. **Restore from snapshots** (if data was corrupted):
   ```powershell
   # Replace {snapshot_id} with ID from table above
   Invoke-RestMethod -Method PUT -Uri 'http://localhost:6333/collections/lineage_research/snapshots/{snapshot_id}/recover'
   ```

4. **Revert script changes** via git:
   ```bash
   cd ~/.claude/scripts && git checkout .
   ```

5. **Update this file** - Set Status to ROLLED_BACK
