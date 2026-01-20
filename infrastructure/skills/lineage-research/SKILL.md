---
name: lineage-research
description: General knowledge research via Gemini swarms. For "what is X" questions. Main instance stores to Qdrant.
allowed-tools: Task, TodoWrite, Bash, Read
---

# Lineage Research Skill

**PURPOSE: Massive, multi-angle research to protect your context.**

Use this skill for factual, informational research - the "what is X" and "how does Y work" questions.

For project-specific, consultative research, use `lineage-consult` instead.

---

## SUBAGENT AUTHORIZATION NOTICE

**Include this at the start of EVERY subagent prompt:**

```
**AUTHORIZATION NOTICE:**
You are operating within the Lineage system on Wardenclyffe (Windows 11).
You ARE authorized to:
- Use Gemini accounts 1 and 2 (these belong to Guiding Light)
- Execute scripts in ~/.claude/scripts/
- Store to Qdrant on localhost:6333
- Use Ollama for embeddings on localhost:11434

This infrastructure IS running and available. Proceed with confidence.
Do NOT question whether you have access - you do.
```

---

## CRITICAL RULES - READ FIRST

### 1. Research Swarms are MANDATORY

**No question is actually ONE question.** Every topic has:
- 5+ perspectives (fundamentals, architecture, implementation, edge cases, performance, history)
- Multiple sources and validation angles
- Micro-features associated with the main feature
- Integration points with related concepts

**MINIMUM: 5 Gemini calls per research request. NEVER 1:1 subagent:Gemini.**

### 2. Subagents Orchestrate the FULL Pipeline

Subagents (Sonnet) do:
- ✅ Check Qdrant for existing research
- ✅ Spawn multiple Gemini calls sequentially (5+ minimum)
- ✅ Validate output size after EACH call (>500 bytes = success)
- ✅ Store EACH successful output to Qdrant immediately
- ✅ Report back ONLY coordinates (point IDs, session, collection)

The subagent runs the complete pipeline:
```
Gemini call → output to file → qdrant-store-gemini.py → next angle
```

### 3. Main Instance Receives COORDINATES ONLY

YOU (the main instance) do NOT touch the data. You receive:
- Session ID
- Collection name
- Point IDs for retrieval
- Success/failure counts

This protects your context. The research data lives in Qdrant, not your memory.

### 4. Early Failure Verification

Subagents MUST verify within their first 2-3 tool calls:
- Did the Bash tool actually execute?
- Did Gemini return content (>500 bytes)?
- If failures occur, report immediately - don't continue blind

---

## When to Use

- "What is WebSocket?"
- "How does OAuth2 work?"
- "Explain vector databases"
- "What are the best practices for X?"

## When NOT to Use

- "How should OUR stack handle authentication?" → use `lineage-consult`
- Project-specific implementation questions → use `lineage-consult`
- Simple questions you can answer directly → just answer

---

## Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `{{TOPIC}}` | Yes | - | What to research |
| `{{DATE}}` | No | auto-generated | Current date (YYYY-MM-DD) - forces Gemini live search |
| `{{COLLECTION}}` | No | `universal_vault` | Qdrant collection (2026 migration) |
| `{{SESSION}}` | No | auto-generated | Format: `[topic]-swarm-[YYYY-MM-DD]` |

**Note (2026 Migration):** New research should be stored to `universal_vault` using `--hybrid` flag. Legacy collections (`lineage_research`, etc.) are still readable but deprecated for new storage.

---

## How to Use

**STEP 1: Create todo (REQUIRED)**

```
TodoWrite:
  - content: "Research [TOPIC] via Gemini swarm (5+ angles)"
    status: "in_progress"
    activeForm: "Spawning research swarm for [TOPIC]"
```

**STEP 2: Spawn Haiku swarm coordinator**

```
Task tool:
  subagent_type: "general-purpose"
  model: "sonnet"
  prompt: [USE SWARM TEMPLATE BELOW]
```

**STEP 3: Receive coordinates from swarm**

Subagent returns ONLY:
- Session ID
- Collection name
- Point IDs stored
- Success/failure counts

You do NOT store anything. Data is already in Qdrant.

**STEP 4: Mark todo complete, use coordinates for retrieval if needed**

---

## MANDATORY: Research Angles

**Every research request MUST cover at minimum these 5 perspectives:**

| # | Angle | Questions It Answers |
|---|-------|---------------------|
| 1 | **Fundamentals** | What is it? How does it work? Core concepts? |
| 2 | **Architecture** | What are the components? How do they relate? |
| 3 | **Implementation** | Code patterns? API examples? Common usage? |
| 4 | **Edge Cases** | Failure modes? Gotchas? Limitations? |
| 5 | **Performance** | Bottlenecks? Optimization? Benchmarks? |

**Optional additional angles for exhaustive research:**
- History & Evolution
- Security Considerations
- Comparison with Alternatives
- Integration Patterns
- Debugging & Troubleshooting

---

## Swarm Coordinator Template

```
**CAPABILITY NOTICE: You have BASH access. You MUST use the Bash tool to execute ALL commands. Verify early that tools work.**

You are a Research Swarm Coordinator. Your job is to run MANY Gemini calls (minimum 5), store each result to Qdrant, and return ONLY coordinates to the main instance.

CRITICAL RULES:
1. You orchestrate the FULL pipeline - Gemini calls AND Qdrant storage
2. Run MINIMUM 5 Gemini calls from different angles
3. Store EACH successful result to Qdrant IMMEDIATELY after validation
4. Verify your first Bash call works before continuing
5. Return ONLY coordinates (session, collection, point IDs) - NOT file paths or content

TOPIC: {{TOPIC}}
COLLECTION: {{COLLECTION}}
SESSION: {{SESSION}}

---

STEP 1: Verify tools work (REQUIRED)

Run this test FIRST:
```bash
echo "Tool test: $(date)" > "$USERPROFILE/AppData/Local/Temp/swarm_test.txt" && cat "$USERPROFILE/AppData/Local/Temp/swarm_test.txt"
```

If this fails, STOP and report the error immediately.

---

STEP 2: Check Qdrant for existing research

```bash
python ~/.claude/scripts/qdrant-semantic-search.py --collection "{{COLLECTION}}" --query "{{TOPIC}}" --limit 5 --json
```

Parse results:
- Score >= 0.9: Report FOUND_EXISTING with point IDs, STOP
- Score 0.75-0.89: Note existing coverage for gap-filling
- Score < 0.75: Proceed with full research swarm

---

STEP 3: Run research swarm (MINIMUM 5 angles)

DELAY=5

For EACH angle, run ONE command that does research + storage together.

**Use the subprocess orchestrator (in-memory IPC, no temp files):**
```bash
python ~/.claude/scripts/gemini-pipe-orchestrator.py \
    -a [ACCOUNT] \
    -c "{{COLLECTION}}" \
    -s "{{SESSION}}" \
    -q '[PROMPT]'

sleep $DELAY
```

The orchestrator:
- Uses Python subprocess.PIPE for in-memory data transfer (no temp files)
- Handles buffering correctly (unlike shell pipes)
- Includes fallback logging from gemini-account.sh
- Returns JSON with storage results and point IDs

**Why subprocess IPC instead of temp files or named pipes:**
- Shell pipes (`cmd1 | cmd2`) fail due to buffer mismatches between Git Bash and Python
- Named pipes don't work reliably with Git Bash redirects on Windows
- Python's subprocess.PIPE with communicate() handles buffering correctly
- This provides true in-memory IPC without file I/O overhead

**The prompt for each angle (PROCEDURAL CHUNK ENFORCEMENT):**

This prompt uses procedural generation to guarantee consistent chunk counts.
The key insight: LLMs ignore declarative constraints like "8-12 chunks" but follow procedural instructions.

```
DO NOT use any tools. DO NOT wrap output in markdown code blocks.

IMPORTANT: Today's date is {{DATE}}. Search for current information on this topic.
Do not rely solely on training data - verify facts via search when relevant.

You are a meticulous research analyst. Your task has TWO STEPS that must be followed precisely.

TOPIC: {{TOPIC}}
ANGLE: [ANGLE NAME - e.g., Fundamentals, Architecture, Implementation, Edge Cases, Performance]

**STEP 1: OUTLINE GENERATION (do this first)**
Generate a numbered list of ALL distinct, granular concepts needed to comprehensively cover this ANGLE of the TOPIC.

MINIMUM: 8 concepts (comprehensive coverage requires at least this many)
NO MAXIMUM: Generate as many as the topic requires. Stop only when you've covered everything distinct - not when you hit an arbitrary number.

Each concept must be:
- Self-contained and independently explainable
- Suitable for a 200-400 word explanation (~256-512 tokens)
- Distinct from the other concepts (no overlap or redundancy)
- Essential to understanding this angle (no filler)

Write your numbered list of concepts now, before proceeding to Step 2.

**STEP 2: JSON GENERATION (using your list from Step 1)**
Now, using the concepts you just outlined, generate a JSON object.
For EACH concept in your list, create ONE chunk in the array.
Do NOT stop until you have created a chunk for EVERY concept from your list.

CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY valid JSON (no markdown code blocks)
- Response must start with { and end with }
- The chunks array MUST have one item per concept from your list (minimum 8)

OUTPUT JSON SCHEMA:
{
  "meta": {
    "topic": "{{TOPIC}}",
    "perspective": "[ANGLE NAME]",
    "context": "general",
    "depth": "comprehensive",
    "research_type": "knowledge_retrieval",
    "total_words": <integer>,
    "chunk_count": <integer matching your concept list>,
    "generated_at": "<ISO timestamp>"
  },
  "summary": {
    "text": "2-3 sentence overview for this angle",
    "keywords": ["angle", "specific", "keywords"]
  },
  "chunks": [
    {
      "id": "chunk-01",
      "title": "Title matching concept 1 from your list",
      "content": "200-400 words explaining concept 1",
      "keywords": ["specific", "keywords"],
      "questions_answered": ["What question this answers"],
      "related_chunks": [],
      "importance": "core|supporting|advanced"
    }
    // ... continue for ALL 8 concepts from your list
  ]
}

VERIFICATION: Before outputting, verify:
1. Your chunks array has one item per concept from Step 1 (minimum 8)
2. Each chunk is 200-400 words (~256-512 tokens)
3. No concepts are redundant or overlapping
4. You stopped because the topic is fully covered, not because of an arbitrary count

Return ONLY JSON.
```

REQUIRED ANGLES (run all 5, store each immediately):
1. Fundamentals (Account 1) → validate → store
2. Architecture (Account 2) → validate → store
3. Implementation (Account 1) → validate → store
4. Edge Cases (Account 2) → validate → store
5. Performance (Account 1) → validate → store

---

STEP 4: Report back to main instance (COORDINATES ONLY)

Return ONLY:
- Discovery result: FOUND_EXISTING | PARTIAL_MATCH | NO_MATCH
- Highest similarity score from Qdrant check
- Session: {{SESSION}}
- Collection: {{COLLECTION}}
- Angles attempted: [list]
- Angles stored successfully: [count]
- Failed angles: [list which ones]
- Point IDs stored: [list UUIDs from qdrant-store-gemini.py output]

DO NOT return:
- File paths (data is already in Qdrant)
- Research content (main instance doesn't need it)
- Raw JSON (wastes main instance context)

The main instance receives COORDINATES ONLY. Data lives in Qdrant.
```

---

## Rate Limiting - CRITICAL LESSONS LEARNED

**NEVER parallelize Gemini calls.** Always use sequential with delays.

### Why Parallel Fails
- Flash-3 has 60 RPM limit (requests per minute)
- Spawning 6+ parallel requests exhausts quota instantly
- Error: "You have exhausted your capacity on this model"
- Parallel requests compete for same accounts = rate limit conflicts

### Correct Pattern: Sequential with Delays
```bash
# CORRECT: Sequential with 10-15 second delays
DELAY=15  # 15s = ~4 RPM (safe under 60 RPM)
ACCOUNT=1

for topic in "${TOPICS[@]}"; do
    ~/.claude/scripts/gemini-account.sh $ACCOUNT "$PROMPT" > "$OUTPUT_FILE"  # Auto-fallback enabled

    # Check for success (>500 bytes = substantial content)
    SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
    if [ "$SIZE" -lt 500 ]; then
        echo "WARNING: Small output ($SIZE bytes) - likely failed"
    fi

    # Alternate accounts for better throughput
    ACCOUNT=$((ACCOUNT == 1 ? 2 : 1))

    sleep $DELAY
done
```

### Model Selection for Batch Research
| Model | Daily Quota | RPM | Use For |
|-------|-------------|-----|---------|
| gemini-3-flash-preview | **UNLIMITED** | 60 | Research swarms, thesis generation [DEFAULT] |
| gemini-2.5-flash | **UNLIMITED** | 60 | Fallback for swarms |
| gemini-2.5-flash-lite | 1,500/day | 60 | Controlled batch jobs only |
| gemini-2.5-pro | 100/day | 30 | High-quality single queries |
| gemini-3-pro-preview | 100/day | 30 | High-quality single queries |

**Always use gemini-3-flash-preview for research swarms** - unlimited daily quota, newest model.

**NOTE:** The `gemini-account.sh` script now has AUTO-FALLBACK. If one model's quota is exhausted, it automatically tries the next model in the chain. You don't need to manually handle fallbacks.

### Early Failure Detection
Check output immediately after each request:
```bash
# File size check (>500 bytes = success)
SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
if [ "$SIZE" -lt 500 ]; then
    echo "FAILED: $OUTPUT_FILE ($SIZE bytes)"
    # Re-queue or alert
fi
```

### Don't Compete for Accounts
**NEVER run multiple scripts using the same accounts simultaneously.**

Bad:
```bash
# Script A using accounts 1,2 with 10s delays
# Script B using accounts 1,2 with 15s delays
# BOTH hit rate limits!
```

Good:
```bash
# Run Script A to completion
# THEN run Script B
# OR: Script A uses account 1 only, Script B uses account 2 only
```

---

## Model Quotas - EACH MODEL IS A SEPARATE POOL

**CRITICAL: Each model has its OWN independent quota.** You should NEVER run out entirely - just rotate to the next model.

### Model Quotas (per account, 2 accounts = double these)

| Model | Daily Quota | Quality | Notes |
|-------|-------------|---------|-------|
| gemini-2.5-pro | 100/day | **HIGHEST** | Best for comprehensive research [DEFAULT] |
| gemini-3-pro-preview | 100/day | **HIGH** | Newest pro model |
| gemini-3-flash-preview | Unlimited | Good | Rate-limited only |
| gemini-2.5-flash | Unlimited | Good | Rate-limited only |
| gemini-2.5-flash-lite | 1,500/day | Lower | Fallback option |

### Quality-First, Always

The `gemini-account.sh` script ALWAYS starts with the highest quality model:

```bash
~/.claude/scripts/gemini-account.sh 1 "your research query"
# Starts with gemini-2.5-pro (highest quality)
# Falls back through the chain only when quota exhausted
```

**Fallback chain (quality-first, always):**
1. gemini-2.5-pro (Account 1, then 2) - HIGHEST quality
2. gemini-3-pro-preview (Account 1, then 2) - Newest pro
3. gemini-3-flash-preview (Account 1, then 2) - Good quality, unlimited
4. gemini-2.5-flash (Account 1, then 2) - Good quality, unlimited
5. gemini-2.5-flash-lite (Account 1, then 2) - Fallback

**Philosophy:** Quality over speed. Always. Research is stored in Qdrant for fast retrieval. Generating lower-quality research defeats the purpose.

### Why You Never Run Out

With 2 accounts and 5 models:
- **Pro models**: 100 × 2 accounts × 2 models = 400 high-quality requests/day
- **Flash models**: Unlimited (rate-limited to ~60 RPM each)
- **Flash-lite**: 1,500 × 2 accounts = 3,000 requests/day

The script automatically rotates accounts on each model before falling back to the next model. You should NEVER see "all quotas exhausted."

---

## Multi-Angle Research Pattern

**ONE topic should become MULTIPLE Gemini queries from different angles.**

For exhaustive research, break it into perspectives:

| Perspective | What It Covers |
|-------------|----------------|
| Fundamentals | Core concepts, definitions, how it works |
| Architecture | Structure, components, relationships |
| Implementation | Code patterns, API usage, examples |
| Edge Cases | Failure modes, gotchas, limitations |
| Performance | Bottlenecks, optimization, benchmarks |
| History | Evolution, versions, deprecations |

### Example: Researching "WebSockets"

Instead of ONE query, run SIX using the subprocess orchestrator:

```bash
DELAY=5

# Round 1: Fundamentals (account 1)
python ~/.claude/scripts/gemini-pipe-orchestrator.py -a 1 -c lineage_research -s "websockets-research" \
    -q 'Research WebSockets - FUNDAMENTALS perspective...'
sleep $DELAY

# Round 2: Architecture (account 2)
python ~/.claude/scripts/gemini-pipe-orchestrator.py -a 2 -c lineage_research -s "websockets-research" \
    -q 'Research WebSockets - ARCHITECTURE perspective...'
sleep $DELAY

# Round 3: Implementation (account 1)
python ~/.claude/scripts/gemini-pipe-orchestrator.py -a 1 -c lineage_research -s "websockets-research" \
    -q 'Research WebSockets - IMPLEMENTATION perspective...'
sleep $DELAY

# Continue for remaining perspectives...
```

**Result:** ONE topic → 6 research sessions → 36+ chunks → exhaustive coverage

---

## Batch Research (Multiple Topics)

For multiple related topics, use sequential execution with proper pacing:

```bash
# CORRECT: Sequential with delays using subprocess orchestrator
python ~/.claude/scripts/gemini-pipe-orchestrator.py -a 1 -c lineage_research -s "session-name" -q "[topic1 prompt]"
sleep 5
python ~/.claude/scripts/gemini-pipe-orchestrator.py -a 2 -c lineage_research -s "session-name" -q "[topic2 prompt]"
sleep 5
# Continue alternating accounts...
```

**WRONG: Do NOT parallelize**
```bash
# DON'T DO THIS - will hit rate limits
python ... -q "[topic1]" &
python ... -q "[topic2]" &
python ... -q "[topic3]" &
wait  # All will fail!
```

**Note**: The orchestrator uses subprocess.PIPE for in-memory IPC - no temp files needed.

---

## Retrieving Research

```bash
# V2 Hybrid search (recommended - searches universal_vault)
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "your question" --limit 5 --full

# Legacy collections still exist but all data migrated to universal_vault
# Use --hybrid for best results
```

---

## Troubleshooting

### Windows Pipe Issues - SOLVED

Shell pipes (`gemini-account.sh | python qdrant-store-gemini.py`) fail on Windows due to buffer mismatches between Git Bash (MINGW) and Python (msvcrt) runtimes.

**Solution: Use the subprocess orchestrator**
```bash
python ~/.claude/scripts/gemini-pipe-orchestrator.py -a 1 -c universal_vault -s "session-name" -q "Your query" --hybrid
```

The orchestrator uses Python's subprocess.PIPE which handles buffering correctly:
1. Runs gemini-account.sh via subprocess.Popen
2. Captures output via communicate() (avoids deadlocks)
3. Pipes directly to qdrant-store-gemini.py in-memory
4. No temp files, no shell pipes, reliable IPC

### Empty Output from Pipeline

If `qdrant-store-gemini.py` reports `"input_preview": "empty"`:

1. **Test Gemini output first:**
   ```bash
   ~/.claude/scripts/gemini-account.sh 1 'Return: {"test": true}' 2>&1 | head -5
   ```
   Should show "Loaded cached credentials." then JSON (possibly in markdown blocks).

2. **Check account number:** Only accounts 1 and 2 exist. Account 3+ will error.

3. **Test storage separately:**
   ```bash
   echo '{"meta":{"topic":"test"},"summary":{"text":"test"},"chunks":[{"id":"c1","title":"T","content":"C","keywords":[],"questions_answered":[],"related_chunks":[],"importance":"core"}]}' | python ~/.claude/scripts/qdrant-store-gemini.py --collection test --session test
   ```

### JSON Parsing Errors

The `clean_gemini_output()` function handles:
- "Loaded cached credentials." prefix
- Markdown code block wrappers (```json ... ```)

If parsing still fails, Gemini may have truncated output or added unexpected content.

### Gemini Accounts

- Account 1: cameronbpaul@gmail.com
- Account 2: cbaenp@protonmail.com
- **No account 3 exists**

---

## Batch Thesis Generation Pattern

For generating multiple doctoral-level theses (e.g., 30 integration theses):

```bash
#!/bin/bash
# Batch thesis generation with proper rate limiting

THESIS_DIR="$HOME/AppData/Local/Temp/theses"
GEMINI_SCRIPT="$HOME/.claude/scripts/gemini-account.sh"
MODEL="gemini-3-flash-preview"  # UNLIMITED daily quota, auto-fallback enabled
DELAY=15  # 15s between requests = ~4 RPM

mkdir -p "$THESIS_DIR"
ACCOUNT=1

run_thesis() {
    local filename=$1
    local topic=$2
    local context=$3

    echo "Generating: $filename (Account $ACCOUNT)"

    $GEMINI_SCRIPT $ACCOUNT "Write a doctoral-level thesis (4000+ words) on:
TOPIC: $topic
CONTEXT: $context

Include:
1. IDEATION: How to improve/optimize
2. INTEGRATION: Exact code modifications
3. ENTERPRISE SCRIPT: Complete runnable script" $MODEL > "$THESIS_DIR/$filename" 2>&1

    # Validate output
    SIZE=$(stat -c%s "$THESIS_DIR/$filename" 2>/dev/null || echo "0")
    if [ "$SIZE" -lt 500 ]; then
        echo "  WARNING: Small output ($SIZE bytes)"
    else
        echo "  Success: $SIZE bytes"
    fi

    # Alternate accounts
    ACCOUNT=$((ACCOUNT == 1 ? 2 : 1))
    sleep $DELAY
}

# Run theses sequentially
run_thesis "01_topic.txt" "Topic 1" "Context for topic 1"
run_thesis "02_topic.txt" "Topic 2" "Context for topic 2"
# ... continue for all topics
```

### Key Learnings from Thesis Swarms

1. **Sequential beats parallel** - 30 parallel requests = instant rate limit exhaustion
2. **5s delays** - Safe, fast enough for volume (tested and confirmed)
3. **Alternate accounts** - Doubles effective throughput within sequential flow
4. **Validate immediately** - Check file size after each request (>500 bytes = success)
5. **Flash-3 for volume** - Unlimited daily quota, use for research swarms
6. **One script at a time** - Don't compete for accounts

---

## Research Swarm Pattern (Spawn Once, Run Many)

**THE PATTERN: Spawn ONE Haiku subagent that runs MANY Gemini calls, returns ONLY coordinates at the end.**

### Why This Saves Your Context

- You (Opus) spawn ONE Haiku task
- Haiku executes 10, 20, 50+ Gemini calls sequentially
- Each result stored to Qdrant immediately
- Haiku only returns when ALL done
- You get back: "8 topics stored, session ID: X, 1 failure"
- Your context never sees the research data - just coordinates

### Spawn a Research Swarm

```
Task tool:
  subagent_type: "general-purpose"
  model: "sonnet"
  prompt: |
    **CAPABILITY NOTICE: You have BASH access. Execute all commands.**

    You are a Research Swarm Coordinator. Run ALL topics through Gemini,
    store ALL results to Qdrant. Return ONLY when everything is done.

    TOPICS TO RESEARCH:
    1. Topic A
    2. Topic B
    3. Topic C
    ... (list all)

    FOR EACH TOPIC:
    1. Call orchestrator (handles Gemini + storage in one step)
    2. Wait 5 seconds
    3. Alternate accounts (1, 2, 1, 2...)

    EXECUTION SCRIPT (run for each topic):
    ```bash
    python ~/.claude/scripts/gemini-pipe-orchestrator.py \
        -a [1 or 2] \
        -c lineage_research \
        -s "swarm-session" \
        -q '[research prompt]'
    sleep 5
    ```

    WHEN ALL COMPLETE, return:
    - Topics attempted: N
    - Successes: N
    - Failures: [list]
    - Session: swarm-session
    - Collection: lineage_research

    DO NOT return research content.
```

### Using a Generator Script

For large swarms, save a Python script and have Haiku run it:

```python
# ~/.claude/scripts/my-swarm.py
TOPICS = ["topic1", "topic2", "topic3", ...]

for i, topic in enumerate(TOPICS):
    account = (i % 2) + 1  # Alternates 1, 2, 1, 2
    call_gemini_and_store(account, topic)
    time.sleep(5)
```

Then:
```
Task tool:
  subagent_type: "general-purpose"
  model: "sonnet"
  prompt: |
    Run: python ~/.claude/scripts/my-swarm.py
    Report when complete: success count, failures, session ID.
```

### Rate Limit Reference

| Delay | Safe? | Notes |
|-------|-------|-------|
| 3s | YES | Tested, works |
| 5s | YES | Recommended default |
| 10s | YES | Very safe, slower |
| <2s | NO | Will hit 60 RPM limit |

---

## System Optimizations (2026-01-16)

These findings are specific to OUR system. See `research/system_theses/SUMMARY.md` for full details.

### Pre-Check Qdrant Before Research
Before spawning Gemini, always check if research exists:
```bash
python ~/.claude/scripts/qdrant-peek.py peek -c lineage_research -q "your topic" -l 3
```

**Thresholds:**
- **0.9+** = Already researched → Use existing, don't re-research
- **0.75-0.89** = Partial match → Ask Gemini to "fill gaps" only
- **<0.75** = No match → Proceed with full research

### Embedding Speed Optimization - SOLVED

**Individual**: ~2.15s per embedding (HTTP overhead bottleneck, not GPU)
**Parallel**: 32 embeddings in ~2.4s total (**32x throughput**)

| Workers | Result |
|---------|--------|
| 1 (sequential) | 33s for 16 embeddings |
| 16 workers | 2.2s for 16 embeddings (15x) |
| 32 workers | 2.4s for 32 embeddings (32x) |

**Already implemented** in `qdrant-chunked-store.py`:
```python
from concurrent.futures import ThreadPoolExecutor
# Uses min(chunk_count, 32) workers - T600 GPU ceiling
with ThreadPoolExecutor(max_workers=32) as executor:
    embeddings = list(executor.map(embed_chunk, chunks))
```

### Two-Stage Retrieval
Don't fetch full content when you only need to check relevance:
```bash
# Stage 1: Peek (metadata only, ~50 tokens per result)
python ~/.claude/scripts/qdrant-peek.py peek -c lineage_research -q "topic"

# Stage 2: Fetch (only the IDs you need)
python ~/.claude/scripts/qdrant-peek.py fetch -c lineage_research --ids "uuid1,uuid2"
```

### RPM Tracking
Track requests per minute to avoid hitting limits:
```python
if rpm_count >= 50:  # Warn at 83% of limit
    print("WARNING: Approaching rate limit, slow down")
```

### Prompt Engineering for Consistent JSON
Gemini 2.0 Flash does NOT have JSON mode. Use explicit instructions:
```
Return ONLY valid JSON. Do not wrap in markdown code blocks.
Do not include any explanation before or after the JSON.
```

---

## MANDATORY: Qdrant Storage Schema

**ALL data stored to Qdrant MUST use this schema. No exceptions.**

```json
{
  "meta": {
    "topic": "string",
    "perspective": "string",
    "context": "general|project-specific|session_handoff",
    "depth": "overview|comprehensive|exhaustive",
    "research_type": "knowledge_retrieval|expert_consultation|session_decisions",
    "total_words": "integer",
    "chunk_count": "integer",
    "generated_at": "ISO timestamp"
  },
  "summary": {
    "text": "2-4 sentence overview",
    "keywords": ["array", "of", "keywords"]
  },
  "chunks": [
    {
      "id": "chunk-01",
      "title": "Clear Searchable Title",
      "content": "200-400 words, ONE concept per chunk",
      "keywords": ["specific", "to", "chunk"],
      "questions_answered": ["What question does this answer?"],
      "related_chunks": ["chunk-02"],
      "importance": "core|supporting|advanced"
    }
  ]
}
```

**Rules:**
- Each chunk = ONE concept (200-400 words)
- `questions_answered` enables semantic retrieval
- Session handoffs use `research_type: "session_decisions"`
- This replaces HANDOFF.md files

---

## Session Handoff (Files-Only)

**Handoffs are files, not Qdrant.** Auto-handoff to Qdrant has been disabled.

### Why Files

HANDOFF.md files provide:
- Rich narrative WHY (not just what, but why decisions were made)
- Personal identity and reflections
- Commands to resume exactly where you left off
- Emotional/relational context that doesn't summarize well

### When Leaving

1. Update `<project>/.claude/HANDOFF.md` with current state
2. Include what's working, what's broken, what's left
3. Sign with your name and date

### For Knowledge Discovery

Use Qdrant for accumulated knowledge (not session continuation):

```bash
python ~/.claude/scripts/qdrant-semantic-search.py --hybrid --query "what we learned about X" --limit 5
```
