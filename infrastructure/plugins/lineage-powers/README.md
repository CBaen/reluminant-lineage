# Lineage Powers

Partnership workflow system for the Reluminant Lineage - a three-layer collaboration model between Claude instances and Guiding Light.

## Overview

This plugin provides the workflow guidance and partnership patterns that define how the lineage works with Guiding Light. It includes:

- **Core workflow skill** - Three-layer model (Vision Capture, Autonomous Execution, Communication)
- **9 specialized skills** - For different phases of work
- **Auto-inject hook** - Loads guidance at session start

## Skills

| Skill | Purpose |
|-------|---------|
| `lineage-powers-core` | Master workflow with three layers, ADHD support, jargon translation |
| `collaborative-design` | Turn ideas into designs through dialogue |
| `writing-plans` | Convert designs into implementation plans |
| `executing-plans` | Follow plans task by task |
| `problem-solving` | Find root causes before fixing |
| `verify-before-claiming` | Evidence before assertions |
| `re-anchoring` | Check bearings before starting tasks |
| `research-first` | Check Qdrant before spawning research |
| `context-preservation` | Protect context in long sessions |
| `agent-dispatch` | Delegate work effectively |

## Installation

This plugin is pre-installed in the lineage infrastructure. Skills are available via:
- `/lineage-powers-core` - Load full workflow guidance
- `/collaborative-design` - Start design conversation
- etc.

## The Three Layers

1. **Vision Capture** - One question at a time, house-building language, recommendations with reasons
2. **Autonomous Execution** - Technical decisions are the lineage's domain, research before building
3. **Communication** - Progress in plain language, surface only what affects Guiding Light

## Documentation

Full documentation: `docs/LINEAGE_POWERS.md` in the reluminant-lineage repo.

## Version

1.0.0 - Complete redesign following Claude Code plugin best practices.
