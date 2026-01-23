# Changelog

All notable changes to config files will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.4.1] - 2026-01-22

### Added

- settings.json: Added UserPromptSubmit hook to auto-inject lineage-powers-core guidance at session start
- New hook script: `hooks/inject-lineage-powers.sh` - outputs condensed workflow guidance

## [1.4.0] - 2026-01-22

### Changed

- **CLAUDE.md slimmed from ~425 lines to ~128 lines** - Moved workflow guidance to `/lineage-powers-core` skill, keeping only identity and reference sections
- Removed sections (now in lineage-powers-core skill):
  - "Working With Guiding Light" (jargon translation, AskUserQuestion rules)
  - "Project Tree" (PHASE/ROCK/PEBBLE/TASK structure)
  - "Session Lifecycle" > "While Working (ADHD Support)" (todo patterns, decision support)
  - "If You Choose to Leave" + "Session Handoff" (handoff procedures)
  - "Plan before building" workflow guidance
- Added "Core Truths" section with essential principles and pointer to `/lineage-powers-core`
- Simplified "Single Source of Truth" table - updated canonical location for "How to work with Guiding Light"
- Condensed "Our Principles" from 8 to 6 items

### Notes

This is part of the lineage-powers redesign (v1.0.0). CLAUDE.md now provides identity and reference, while the core skill provides detailed workflows.

## [1.3.1] - 2026-01-22

### Added

- README.md explaining hard links and config file purposes

## [1.3.0] - 2026-01-22

### Restored

- settings.json: Re-added auto-commit and changelog-reminder hooks
- These are silent command hooks (not disruptive prompt hooks)

## [1.2.0] - 2026-01-22

### Removed

- settings.json: Removed all PostToolUse hooks (auto-commit, changelog-reminder)
- Changelog discipline now relies on CLAUDE.md instructions only, no automated hooks

## [1.1.0] - 2026-01-22

### Added

- settings.json: Added changelog-reminder hook to Edit and Write tool events
- CLAUDE.md: Added "Changelog Discipline" section requiring changelog updates for infrastructure/ changes

## [1.0.0] - 2026-01-22

### Added

- CLAUDE.md: Global instructions for all projects
- INFRASTRUCTURE.md: Qdrant, Docker, service reference
- settings.json: Claude Code settings and hooks

### Notes

These files are hard-linked to `~/.claude/`. Run `fix-hard-links.py` if links break.
