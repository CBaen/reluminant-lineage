# Changelog

All notable changes to config files will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
