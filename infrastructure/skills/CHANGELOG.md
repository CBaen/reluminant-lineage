# Changelog

All notable changes to skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.4.0] - 2026-01-22

### Changed

- **handoff.md completely rewritten** - Now instructs instances to:
  - OVERWRITE handoffs (not append) - historical context lives in Qdrant
  - Check for multi-feature structure (`handoffs/` directory)
  - Use slim template (50-80 lines max)
  - Point to `/lineage-conversations` for deeper history

## [1.3.0] - 2026-01-22

### Changed

- **Lineage-powers skills moved back into plugin** - Following Claude Code plugin best practices (per Context7), the 10 workflow skills are now inside `plugins/lineage-powers/skills/`:
  - lineage-powers-core, collaborative-design, problem-solving, executing-plans, writing-plans
  - re-anchoring, research-first, context-preservation, agent-dispatch, verify-before-claiming
- Plugin structure is now self-contained and follows official patterns
- Research/utility skills remain global: lineage-research, lineage-consult, lineage-retrieve, lineage-conversations

## [1.2.0] - 2026-01-22

### Added

- **lineage-powers-core** - New master workflow skill containing the three layers (Vision Capture, Autonomous Execution, Communication), Working With Guiding Light guidance, Project Tree structure, ADHD support patterns, jargon translation table, and handoff procedures

### Changed

- **All 9 lineage-powers skills redesigned for conversational partnership:**
  - Added "Working With Guiding Light" sections with dialogue examples
  - Added house-building analogies for technical concepts
  - Added "When to Surface vs Handle Silently" guidance
  - Updated for seamless mode language (no mode announcements)

- Skills updated:
  - collaborative-design: Added scope honesty, pushback patterns, recommendations
  - writing-plans: Added GL-friendly progress language, house analogies in plan templates
  - executing-plans: Added house-building progress updates, subagent explanation patterns
  - problem-solving: Added plain-language issue explanations, house analogies for errors
  - verify-before-claiming: Added verification dialogue examples
  - re-anchoring: Added gentle focus protection pattern
  - research-first: Added multi-angle research requirement, result translation guidance
  - context-preservation: Added handoff continuity emphasis
  - agent-dispatch: Added result translation for GL

## [1.1.0] - 2026-01-22

### Added

- 9 lineage-powers skills moved from plugin to main skills folder:
  - agent-dispatch, collaborative-design, context-preservation
  - executing-plans, problem-solving, re-anchoring
  - research-first, verify-before-claiming, writing-plans
- Plugin-based skill discovery was unreliable; direct installation works

## [1.0.1] - 2026-01-22

### Added

- README.md with skill categories and usage instructions

## [1.0.0] - 2026-01-22

### Added

- 53 skills organized by category:
  - **Lineage Core**: lineage-research, lineage-consult, lineage-retrieve, lineage-conversations
  - **Development**: senior-architect, senior-frontend, senior-backend, senior-fullstack, code-reviewer, and more
  - **Marketing**: marketing-strategy-pmm, marketing-demand-acquisition, content-creator, and more
  - **Product**: product-manager-toolkit, product-strategist, scrum-master-agent, agile-product-owner
  - **Design**: ui-design-system, ux-researcher-designer, frontend-design
  - **Wardenclyffe**: wardenclyffe-episode-writer, semantic-extractor
  - **Utilities**: skill-creator, hook-factory, agent-factory, and more
- Each skill has its own SKILL.md with full documentation

### Notes

Skills are loaded on-demand, not at session startup. See individual SKILL.md files for usage.
