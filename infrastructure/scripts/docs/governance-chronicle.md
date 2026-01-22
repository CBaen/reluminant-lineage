# governance_chronicle.py

Store governance model actions to Qdrant.

## What It Does

Records governance model actions (research, proposals, votes, rankings, eliminations, file operations) to Qdrant for audit trail and analysis.

## Usage

```python
from governance_chronicle import GovernanceChronicle

chronicle = GovernanceChronicle()

# Record research
chronicle.record_research(topic, findings, session)

# Record vote
chronicle.record_vote(proposal_id, vote, rationale, session)

# Record file operation
chronicle.record_file_op(operation, path, session)
```

## Action Types

| Type | Purpose |
|------|---------|
| research | Knowledge gathering |
| proposal | Suggested changes |
| vote | Decision on proposal |
| ranking | Priority ordering |
| elimination | Removal decision |
| file | File system operation |

## Dependencies

- `qdrant-client`
- Ollama (embeddings)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
