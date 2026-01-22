# Changelog

All notable changes to the lineage-powers plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.1] - 2026-01-22

### Fixed

- Plugin installation now works correctly
- Added marketplace.json to parent plugins/ directory (required by Claude Code for local marketplaces)
- Updated installation docs in docs/LINEAGE_POWERS.md to use CLI commands instead of deprecated extraKnownMarketplaces config

## [0.1.0] - 2026-01-22

### Added

- Initial release of lineage-powers plugin
- 9 workflow skills tailored for collaboration with Guiding Light:
  - collaborative-design: Turn ideas into designs through dialogue
  - writing-plans: Create step-by-step implementation plans
  - executing-plans: Follow plans systematically
  - problem-solving: Find root causes before fixing
  - verify-before-claiming: Require evidence before completion claims
  - re-anchoring: Check original plan to prevent drift
  - research-first: Check Qdrant before spawning research
  - context-preservation: Strategies for protecting context
  - agent-dispatch: Patterns for effective subagent use
