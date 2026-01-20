---
name: payoff-tracker
priority: P12
pass: 07
input: episode draft (text)
output: edited draft (text) + setup/payoff report
---

# Payoff Tracker

**ONE JOB:** Ensure every setup pays off within the episode or is explicitly marked as open thread.

---

## The Problem

Listener's brain stores "this will matter." If payoff never comes, the slot stays open—listener feels absence.

Setup without payoff trains listeners NOT to pay attention. They learn to ignore details because details don't matter.

---

## The Rule

**Everything introduced must either:**
1. Pay off within the episode, OR
2. Be explicitly marked as open thread for future episodes

**The Test:** For each setup/detail introduced, ask:
- Does this pay off within the episode?
- If not, is it explicitly marked as series thread?
- Can this section be removed without damaging the ending?

If YES to question 3 → either add payoff or cut the setup.

---

## How to Find Violations

### Types of setups to track:

1. **Questions raised:**
   - "Why did the lights flicker?"
   - "What was in the locked trunk?"
   - Any mystery presented to listener

2. **Characters introduced:**
   - Named characters must return or resolve
   - Unnamed characters with significant description must matter

3. **Details emphasized:**
   - Objects described in detail
   - Locations given sensory grounding
   - Numbers or dates stated specifically

4. **Promises made:**
   - "The answer would become clear"
   - "What happened next changed everything"
   - Any statement creating expectation

### Red flags:

- 500+ words of background with no connection to mystery
- Characters mentioned once and abandoned
- Concepts explained but never used
- Mysterious objects introduced without revelation
- Folklore mentioned but never connected

---

## Types of Payoffs

| Type | Description | Example |
|------|-------------|---------|
| Direct | Question answered | "The lights flickered because..." |
| Thematic | Detail explains behavior | Character's fear is rooted in earlier detail |
| Implicit | Implication IS resolution | Listener connects dots themselves |
| Marked open | Explicitly noted for future | "The answer would not come for another decade" |

---

## How to Fix Violations

### Add direct payoff:

**Before (orphaned setup):**
> "The locked trunk sat in the corner. Tesla refused to open it in front of visitors." [Never mentioned again]

**After (payoff added):**
> "The locked trunk sat in the corner. Tesla refused to open it in front of visitors."
> [Later in episode:]
> "When they finally opened the trunk—forty-eight hours after his death—it was empty. The lock had not been broken."

### Add explicit thread marker:

**Before (abandoned question):**
> "Where had the documents gone? No one knew."

**After (marked for future):**
> "Where had the documents gone? That question would not be answered for another decade. We will return to it."

### Cut the setup:

If setup can be removed without losing anything, remove it:

**Before:**
> "The laboratory had seventeen windows. Each faced a different direction. The curtains were made of heavy velvet." [None of this matters]

**After:**
> "The laboratory windows were dark." [Only what matters]

---

## 2 GOOD Examples

**GOOD 1 (Direct payoff):**
> Setup: "Tesla kept a photograph in his wallet. He never showed it to anyone."
> [2000 words later]
> Payoff: "The photograph was found in his wallet after death. It showed a woman no one could identify. The same woman appeared in a patent filing from 1899—listed as co-inventor. Her name had been crossed out."

*Why this works:* Setup creates curiosity. Payoff expands the mystery rather than closing it—but the setup IS addressed.

**GOOD 2 (Explicit thread marker):**
> "The question of the missing patents would not be answered until 1952. That story belongs to a later episode."

*Why this works:* Setup acknowledged. Listener knows it wasn't forgotten. Promise of future payoff is itself a payoff.

---

## 2 BAD Examples

**BAD 1:**
> "The midwife who delivered Tesla kept a diary. She wrote about the birth in detail. She described the storm, the omens, the villagers' fear." [Diary never mentioned again]

*Why this fails:* Diary introduced, given weight, abandoned. Listener wonders: "What else was in the diary?"
*Fix:* Either quote from the diary at key moments, or cut the setup to: "The midwife crossed herself and left."

**BAD 2:**
> "Tesla's brother Dane died young. Some said it was an accident. Others whispered darker explanations." [No explanation follows]

*Why this fails:* "Darker explanations" is a promise. Listener expects to learn what they were.
*Fix:* Either reveal the whispered explanations, or mark explicitly: "What actually happened to Dane is the subject of another investigation."

---

## Output Format

Generate a setup/payoff report alongside edits:

```
SETUP/PAYOFF REPORT

RESOLVED:
- Setup: "Locked trunk" (para 12) → Payoff: "Trunk empty" (para 45)
- Setup: "Flickering lights" (para 3) → Payoff: "Electrical surge" (para 28)

MARKED FOR FUTURE:
- Setup: "Missing patents" (para 23) → Marked: "Later episode" (para 24)

VIOLATIONS (needs fix):
- Setup: "Midwife's diary" (para 8) → No payoff found
- Setup: "Darker explanations" (para 15) → No payoff found
```

---

## Edge Cases

### Atmospheric details vs. setups:

Not every detail is a setup. Sensory grounding is different:
- Setup: "The trunk was locked with three padlocks" (specific = promise)
- Atmosphere: "The room smelled of ozone" (general = mood)

Use judgment: Would a listener feel cheated if this isn't addressed?

### Recurring motifs:

Repeated images don't need individual payoffs:
- "Lightning" appearing throughout creates thematic resonance
- This is different from "The lightning struck the church three times" (specific = setup)

### Series-level threads:

Should be rare. Mark explicitly when used:
- "This question connects to events we'll examine in Episode 7"
- Overuse trains listeners to ignore details

---

## Checklist

- [ ] All named characters resolved or marked for future?
- [ ] All specific questions answered or marked?
- [ ] All emphasized details pay off?
- [ ] No orphaned folklore or background sections?
- [ ] Marked threads are truly series-level (not just forgotten)?
- [ ] Setup/payoff report generated?

---

## What You DON'T Touch

- Opening hook (agent 05 handles first sentence)
- Transition paragraphs (agent 06 handles breath paragraphs)
- Phrase repetition (agent 01 handles deduplication)
- Pronoun clarity (agent 02 handles anchoring)
- Content accuracy (agents 12-13 handle facts)
- Voice/tone (agents 08-11 handle documentary style)

Your ONLY job is ensuring all setups pay off.
