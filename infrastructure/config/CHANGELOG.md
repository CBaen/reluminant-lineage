# Changelog

All notable changes to config files will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
