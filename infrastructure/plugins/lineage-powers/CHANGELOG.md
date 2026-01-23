# Changelog

All notable changes to the lineage-powers plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-01-22

### Changed

- **Complete redesign for conversational partnership** - Transformed from developer-focused skills to a system designed for Guiding Light (non-technical visionary)
- **New core skill: lineage-powers-core** - Master skill containing the three layers (Vision Capture, Autonomous Execution, Communication), Working With Guiding Light guidance, Project Tree structure, ADHD support patterns, and handoff procedures
- **CLAUDE.md slimmed to ~128 lines** - Moved workflow guidance to core skill, keeping only identity and reference sections
- **All 9 skills updated with partnership layers:**
  - Added "Working With Guiding Light" sections with dialogue examples
  - Added house-building analogies for technical concepts
  - Added "When to Surface vs Handle Silently" guidance
  - Removed mode announcements for seamless flow

### Added

- **Jargon translation table** in core skill - Technical terms mapped to plain-language explanations
- **Scope honesty** - Guidance on recommending simpler paths when quality isn't sacrificed
- **Pushback patterns** - How to respectfully disagree when ideas conflict with good construction
- **Gentle focus protection** - Soft check-ins when conversation drifts
- **Multi-angle research requirement** - Gather from multiple perspectives, not just one source
- **Handoff continuity emphasis** - New instances prove understanding before asking GL to re-explain

### Design Principles

The redesign follows these principles from the design doc:
1. **Seamless flow** - Instance reads situation and shifts naturally, no visible modes
2. **Conversational partnership** - Back and forth shaping the vision, then instance handles building
3. **Impact-based surfacing** - Small issues handled silently, significant issues surfaced in plain language

## [0.2.0] - 2026-01-22

### Changed

- **Skills moved to `infrastructure/skills/`** - Plugin skill discovery was unreliable; skills now live in main skills folder where they work correctly
- Removed `skills/` subfolder from plugin (duplicates removed)
- Plugin structure retained for potential future use

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
