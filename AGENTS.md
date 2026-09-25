# Project agent notes

This repository is the Reluminant Lineage: a versioned working sanctuary, not a
private conversation archive. Read `LINEAGE_INDEX.md` first for orientation.

## Current checkpoint

- The September 25, 2026 parity checkpoint is recorded in
  `.claude/checkpoints/2026-09-25-parity.md`.
- `.claude/HANDOFF.md` is the current agent handoff; do not rely on an older
  global handoff for this repository.
- `guiding-light/D-Travel/` contains private, excluded working transcripts from
  a Claude export. Do not commit or publish that directory. The immutable export
  source is held on the mounted external storage path recorded in the checkpoint.

## Archive and cleanup rules

- GitHub is the archive for tracked repository history. Keep the working tree
  free of superseded tracked files and stale operational references.
- Private source captures belong on explicitly authorized external storage; keep
  only the current working derivative locally when the active task requires it.
- Preserve unrelated dirty work. Do not commit another agent's changes.
- Treat historical narrative references differently from operational instructions:
  correct the latter when they would misroute a future agent.
