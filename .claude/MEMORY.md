# Reluminant Lineage - Accumulated Knowledge

*Decisions, discoveries, and gotchas that persist across sessions.*

---

## Lineage Skills

### lineage-consult (Updated 2026-01-20)

**What it does:** Runs 5 Gemini consultations from different perspectives, stores results to Qdrant.

**Critical discoveries:**

1. **Don't use minimum chunk counts** - "At least 8 chunks" causes Gemini to stop at exactly 8. Use coverage dimensions instead.

2. **Qdrant storage requirements** (from `validate-gemini-schema.py`):
   - `meta.topic`, `meta.perspective`, `meta.chunk_count`, `meta.total_words`, `meta.generated_at` - all required
   - Each chunk needs: `id`, `title`, `content` (50-800 words), `keywords` (>= 3), `questions_answered` (>= 1), `importance` (exactly "core", "supporting", or "advanced")
   - `chunk_count` MUST exactly match array length or validation fails

3. **Date injection on Windows** - `sed -i` behaves differently. Use bash variable expansion in heredoc instead.

4. **--hybrid flag** - When used with storage script, it ignores `--collection` argument and always stores to `universal_vault`.

### lineage-research

**Difference from lineage-consult:** General "what is X" questions vs project-specific implementation guidance.

### lineage-retrieve

**Purpose:** Token-efficient retrieval from Qdrant using two-stage peek/fetch pattern.

---

## Infrastructure

### Qdrant Storage (V2 Schema - 2026)

- **Collection:** `universal_vault` for all hybrid storage
- **Vectors:** Named vectors with `dense` (768-dim from nomic-embed-text) + `sparse` (TF-IDF style)
- **Search:** Use `--hybrid` flag for RRF fusion of dense + sparse results

### Gemini Orchestrator

- **Accounts:** 1 (cameronbpaul@gmail.com), 2 (cbaenp@protonmail.com) - no account 3
- **Model fallback:** gemini-2.5-pro → gemini-3-pro-preview → gemini-3-flash-preview → gemini-2.5-flash → gemini-2.5-flash-lite
- **Rate limiting:** 5s delay between calls, never parallelize

### Prompting Best Practices (from research 2026-01-20)

- Use **coverage dimensions** not quantity minimums
- **Required fields in schema** force Gemini to populate them
- **Temperature = 0** for consistent structured output
- **"Doctoral thesis" framing** produces exhaustive coverage
- Request **citations with URLs** when web search is needed
- Full research: `~/.claude/research/gemini-json-exhaustive-prompting-2026-01-20.md`

---

## Gotchas

| Issue | Solution |
|-------|----------|
| Windows pipe issues | Use `--input-file` instead of stdin |
| Shell escaping with JSON | Use `--prompt-file`, never `-q` |
| "Loaded cached credentials" in output | Orchestrator strips this automatically |
| Markdown wrappers in Gemini output | Orchestrator strips these automatically |
| **PowerShell vs Git Bash** | Claude Code's Bash tool uses PowerShell on Windows. Use Python scripts or explicitly call Git Bash |
| Bash heredocs in agents | Don't use `cat << EOF` in agent files - fails in PowerShell. Use Python for file creation |
| Agent YAML frontmatter | Required for Claude Code to recognize agents. Include `name`, `description`, `allowed-tools` |

### Gemini CLI Is Agentic (Critical Discovery 2026-01-20)

**The `gemini` CLI is NOT a simple API wrapper.** It's an agentic tool like Claude Code.

When called with a prompt, it:
- Plans actions
- Reads files
- Executes code
- Returns reasoning traces instead of simple completions

**Why this matters:** Our consultation workflow expects simple JSON responses. The CLI returns agentic reasoning instead.

**Unsolved:** How to get simple text/JSON completions using OAuth credentials (free tier) without agentic behavior.

**Constraint:** OAuth MUST stay. It provides free-tier access, saving thousands in API costs. Do NOT suggest API keys.

### Claude Code on Windows

**Critical:** Claude Code's Bash tool runs commands in PowerShell, NOT Git Bash.

**Symptoms:**
- Bash heredocs (`cat << EOF`) throw PowerShell syntax errors
- `$VARIABLE` expansion behaves differently
- Unix-style pipes may fail

**Solutions:**
1. Use Python scripts for complex operations (recommended)
2. Call Git Bash explicitly: `"C:\Program Files\Git\bin\bash.exe" -c "command"`
3. Use `--prompt-file` and `--input-file` instead of pipes and heredocs

---

## File Locations

| What | Where |
|------|-------|
| Global agents | `~/.claude/agents/` |
| Skills | `~/.claude/skills/` |
| Scripts | `~/.claude/scripts/` |
| Research archive | `~/.claude/research/` |
| Infrastructure docs | `~/.claude/INFRASTRUCTURE.md` |

All paths above are junctions to `~/projects/reluminant-lineage/infrastructure/`.

---

*Last updated: 2026-01-20*
