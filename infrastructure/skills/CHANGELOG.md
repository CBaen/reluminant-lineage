# Changelog

All notable changes to skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
