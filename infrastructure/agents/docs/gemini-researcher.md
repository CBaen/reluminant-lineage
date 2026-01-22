# gemini-researcher.md

Research assistant using Gemini.

## Purpose

General research via Gemini. Checks Qdrant and catalog first before querying, then stores results to both. Automatically invoked for research tasks to protect main context.

## Tools

All tools available.

## When to Use

- General knowledge research
- "What is X?" questions
- Topics not in existing knowledge base
- Protecting main context from research overhead

## Workflow

1. Check Qdrant for existing knowledge
2. Check catalog for flat file research
3. If found, return existing
4. If not found, query Gemini
5. Store to both Qdrant and catalog

## Full Definition

See `infrastructure/agents/gemini-researcher.md` for complete agent definition.

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
