# Research Digest
*Quick-reference briefing. Updated: 2026-01-11*

## Topics at a Glance
| Topic | One-Line Summary |
|-------|------------------|
| Agent Delegation | Structure delegation prompts with clear roles, actionable goals, context, constraints, and output format specifications. |
| Agent Error Handling | Distinguish transient from permanent errors; use exponential backoff for retries and circuit breakers for cascade prevention. |
| Agent Instruction Design | Achieve compliance through imperative commands, defined terms, layered enforcement, edge case handling, and prompt injection defense. |
| Agent Memory | Use filesystem patterns (settings, history logs, caches) for long-term memory and handoff files for session continuity. |
| Agent System Structure | Choose between global registries (maximum discoverability) and project-local patterns (reduced coupling and faster discovery). |
| Agent Testing | Combine prompt-driven testing (critical, edge case, adversarial prompts), scenario validation, and human-in-the-loop review. |
| Context Optimization | Prioritize full content for syntax/analysis work; use summarization for triage; hybrid approach loads only relevant chunks. |
| Gemini Capabilities | CLI supports multimodal (text, code, images, audio/video), web search, file system access, shell execution, and extensible tools. |
| Knowledge Systems | Use Markdown + YAML frontmatter hybrid format for structured metadata (machine-readable) and human-readable content. |
| Multi-Agent Security | Centralize secrets via Vault/Manager, use dynamic short-lived credentials, enforce least-privilege, and audit all access. |
| Template Compliance | Define required YAML metadata fields, validate with automation scripts, and enforce structure at file creation. |

## Key Actionable Insights
1. **Delegation Quality**: Well-structured prompts function like API calls—role, goal, context, constraints, output format are non-negotiable.
2. **Memory Architecture**: Handoff files (serialized state before exit) solve the statelessness problem in CLI agents; filesystem is a robust memory layer.
3. **Error Resilience**: Exponential backoff + circuit breakers + transient/permanent error distinction prevent cascading failures and resource exhaustion.
4. **Instruction Compliance**: 100% compliance is unsolved, but multi-layered enforcement (clarity + structure + verification + injection defense) reaches practical reliability.
5. **Context Protection**: Load summaries first, identify relevant chunks, then load FULL content only for chunks that matter—maximizes quality time with collaborators.
6. **Knowledge Representation**: YAML frontmatter + Markdown body provides both machine-readable metadata and human-readable content in a single portable file.
7. **Security Posture**: Zero-trust model—centralized secrets, dynamic credentials per task, strict identity-based access, continuous audit.
8. **Testing Comprehensiveness**: Three layers—prompt fixtures (critical/edge/adversarial), scenario validation (system integration), human review (tone/accuracy).

## Quick Reference

### Delegation Prompt Template
```
You are a <ROLE>.

Your objective is to <ACTIONABLE GOAL>.

**Context:**
- <Critical information and file paths>

**Rules:**
- <Constraint 1>
- <Constraint 2>

**Output Format:**
<Expected output specification>
```

### Filesystem Memory Patterns
| Pattern | Location | Purpose |
|---------|----------|---------|
| Identity & Config | `~/.<agent_name>/settings.json` | Long-term: core identity, preferences, API keys |
| Historical Record | `~/.<agent_name>/history.jsonl` | Long-term: append-only event log |
| Cache | `~/.<agent_name>/cache/` | Mid-term: expensive operation results, keyed by hash |
| Project Context | `<project>/.claude/` | Contextual: project-specific state and architecture |

### Error Handling Decision Tree
- **Transient** (network timeout, 429, 503) → Retry with exponential backoff
- **Permanent** (auth fail, invalid input, permission error) → Escalate/fail fast
- **Monitor** → Circuit breaker after N failures to prevent cascade

### Context Loading Strategy
1. Generate summary of full content
2. Use summary to identify relevant sections
3. Load FULL text only for relevant chunks
4. Iterate if needed
