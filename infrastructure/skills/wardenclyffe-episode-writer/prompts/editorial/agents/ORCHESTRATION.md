# Editorial Pipeline Orchestration

This document explains how to run the 16-agent editorial pipeline for Tesla Mandela Effects episodes.

---

## Architecture Overview

```
GEMINI DRAFT
    ↓
Phase 1: MECHANICAL AUDITS (01-04)
    ↓
Phase 2: STRUCTURAL EDITS (05-07)
    ↓
Phase 3: VOICE EDITS (08-11)
    ↓
Phase 4: ACCURACY CHECKS (12-13)
    ↓
Phase 5: FINAL POLISH (14-16)
    ↓
CLEAN DRAFT
```

---

## The 16 Agents

| Pass | Agent | Priority | Job |
|------|-------|----------|-----|
| 01 | `deduplicator` | NEW | Remove repeated phrases/concepts |
| 02 | `anchor` | P10 | Fix pronoun avalanches, add name anchors |
| 03 | `term-counter` | P5 | Enforce 5-use cap, flag violations |
| 04 | `you-density` | P14 | Move "you" to ending |
| 05 | `opening-hook` | P11 | Ensure first sentence creates vertigo |
| 06 | `transitions` | P9 | Add breath paragraphs at jumps |
| 07 | `payoff-tracker` | P12 | Ensure all setups pay off |
| 08 | `bridge-balancer` | P1 | Enforce 3:1 fact-to-question ratio |
| 09 | `narrator-eraser` | P2 | Remove narrator identity leaks |
| 10 | `jargon-killer` | P4 | Replace terminology with sensation |
| 11 | `dread-enforcer` | P6 | Convert proof to unsettling |
| 12 | `relation-verifier` | P7 | Verify relationships are accurate |
| 13 | `fact-checker` | P8 | Verify ages, dates, distances |
| 14 | `name-economist` | P3 | Reduce names to ≤6 |
| 15 | `clone-detector` | P13 | Flag recycled Episode 1/2 imagery |
| 16 | `sensory-expander` | P4+ | Transform violations into micro-stories |

---

## Running the Full Pipeline

### Method 1: Sequential Claude Editing

For each agent (01 through 16):

1. **Load the agent instructions:**
   ```
   Read: ~/.claude/skills/wardenclyffe-episode-writer/prompts/editorial/agents/[NN]-[name].md
   ```

2. **Load the current draft:**
   ```
   Read: /path/to/current-draft.txt
   ```

3. **Execute the agent's ONE job:**
   - Follow the agent's instructions exactly
   - Make ONLY the changes that agent is responsible for
   - Generate any required reports

4. **Save the output:**
   ```
   Write: /path/to/draft-after-[NN].txt
   ```

5. **Repeat for next agent**

### Method 2: Gemini Flash for Bulk Passes

For mechanical passes (01-04) and some voice passes (08-11), Gemini Flash can handle the edits:

```bash
# Example: Run deduplicator via Gemini
cat draft.txt | ~/.claude/scripts/gemini-account.sh 1 "
$(cat ~/.claude/skills/wardenclyffe-episode-writer/prompts/editorial/agents/01-deduplicator.md)

Apply the above agent instructions to this episode draft:
" > draft-01.txt
```

**Recommended for Gemini:** 01, 02, 04, 08, 09, 10, 11

**Recommended for Claude:** 03 (needs structured output), 05-07 (structural judgment), 12-13 (accuracy verification), 14-16 (series context)

---

## Running Partial Pipelines

### Audio Clarity Fix (Repetition + Pronouns)

If the only problem is audio clarity:

```
Run: 01-deduplicator → 02-anchor
Skip: Everything else
```

### Term Frequency Fix

If term overuse is the main issue:

```
Run: 03-term-counter → 16-sensory-expander
Skip: Everything else
```

### Voice Polish

If tone/perspective needs adjustment:

```
Run: 08-bridge-balancer → 09-narrator-eraser → 10-jargon-killer → 11-dread-enforcer
Skip: Everything else
```

### Accuracy Pass

If facts need verification:

```
Run: 12-relation-verifier → 13-fact-checker
Skip: Everything else
```

### Clone Check

If checking for recycled imagery:

```
Run: 15-clone-detector
Skip: Everything else
```

---

## Pass Order Rationale

### Why This Order?

**Phase 1 (01-04) runs first because:**
- De-duplication must happen before other edits (agent 01)
- Pronoun anchoring touches every paragraph (agent 02)
- Term counting provides flags for later (agent 03)
- "You" density is mechanical, not stylistic (agent 04)

**Phase 2 (05-07) is structural:**
- Opening may need complete rewrite (agent 05)
- Transitions add paragraphs (agent 06)
- Setup/payoff may add or remove content (agent 07)

**Phase 3 (08-11) is voice:**
- These adjust tone without adding/removing major content
- Run after structure is finalized

**Phase 4 (12-13) is verification:**
- Accuracy must be checked on near-final text
- Changes here are corrections, not style

**Phase 5 (14-16) is polish:**
- Name count reduction (agent 14)
- Clone detection is series-level check (agent 15)
- Sensory expansion happens LAST because it needs stable text (agent 16)

---

## Agent Communication

### Agents That Pass Data Forward

| Agent | Passes To | What |
|-------|-----------|------|
| 03 term-counter | 16 sensory-expander | Term violation flags `[TERM:CAT:N]` |
| 07 payoff-tracker | Human/editor | Setup/payoff report |
| 12 relation-verifier | Human/editor | Verification report |
| 13 fact-checker | Human/editor | Verification report |
| 15 clone-detector | Human/editor | Clone report |

### Important: Agent 03 → Agent 16

Agent 03 marks violations like:
```
The [TERM:HOLLOW:7] space where his certainty used to be.
```

Agent 16 transforms these markers into sensory micro-stories.

**If running partial pipeline:** You cannot run 16 without first running 03.

---

## Quality Checkpoints

### After Phase 1 (Mechanical):

- [ ] No phrase repeated 3+ times in 500 words?
- [ ] Names anchored every 2-3 sentences?
- [ ] Term violations flagged for Phase 5?
- [ ] "You" count ≤8 before Metastasis?

### After Phase 2 (Structural):

- [ ] Opening creates vertigo/wrongness?
- [ ] Every jump has breath paragraph?
- [ ] All setups pay off or are marked?

### After Phase 3 (Voice):

- [ ] 3:1 fact-to-question ratio?
- [ ] No "I/we" narrator actions?
- [ ] Medical jargon replaced?
- [ ] Research unsettles, not proves?

### After Phase 4 (Accuracy):

- [ ] All relationships verified?
- [ ] All micro-facts checked?
- [ ] Unverifiable claims made vague?

### After Phase 5 (Polish):

- [ ] ≤6 unusual names?
- [ ] No recycled Episode 1/2 imagery?
- [ ] All term violations transformed?

---

## Troubleshooting

### Agent introduces NEW violations

This shouldn't happen if agents stay in their lanes. If it does:

1. Re-run the earlier agent that handles that violation type
2. Check if the agent document needs clarification
3. Adjust the "What You DON'T Touch" section

### Conflicts between agents

If two agents disagree:

- Structure (05-07) wins over Voice (08-11)
- Accuracy (12-13) wins over everything
- Later agents should not undo earlier agents' work

### Draft quality too low for pipeline

If the Gemini draft has fundamental problems:

1. Consider regenerating with clearer instructions
2. Or: Run a "triage" pass first to address major issues
3. Then proceed with the standard 16-agent pipeline

---

## Episode 2 Reference

For any agent pass, refer to Episode 2 as the gold standard:

```
~/.claude/skills/wardenclyffe-episode-writer/examples/ep2-gold-standard.md
```

Episode 2 demonstrates:
- Sensory expansion patterns
- Audio-first writing that lands in the body
- The craft that makes the series work

---

## Quick Reference

```bash
# Full pipeline (Claude session)
for agent in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16; do
  echo "Running agent $agent..."
  # Load agent doc, apply to draft, save output
done

# Partial pipeline example
agents="01 02 16"  # Just audio clarity + sensory expansion
for agent in $agents; do
  echo "Running agent $agent..."
done
```

---

## Success Criteria

The pipeline is successful when:

1. **No single pass introduces NEW violations** of other priorities
2. **Episode achieves Episode 2 quality standard** across all 14+ priorities
3. **Process is repeatable** for Episodes 4-200 without human intervention

---

*This orchestration guide was created as part of the 16-agent refactoring. Old 5-sweep files are archived in the parent folder.*
