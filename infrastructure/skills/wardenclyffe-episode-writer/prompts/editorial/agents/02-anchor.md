---
name: anchor
priority: P10
pass: 02
input: episode draft (text)
output: edited draft (text)
---

# Anchor

**ONE JOB:** Fix pronoun avalanches by re-anchoring character names every 2-3 sentences.

---

## The Problem

Text readers can glance back. Audio listeners only move forward. Nine consecutive "she" sentences = listener loses track of WHO.

This is the #1 audio clarity problem. Listeners spend mental energy asking "Wait, who is 'he'?" instead of absorbing the story.

---

## The Rule

**Re-anchor the character's name every 2-3 sentences. Never let pronouns run for more than 3 sentences without a name.**

Pattern: Name → Pronoun → Pronoun → Name → Pronoun → Name

---

## How to Find Violations

1. **Count consecutive pronoun sentences:**
   - Any sequence of 4+ sentences using only he/him/his
   - Any sequence of 4+ sentences using only she/her/hers
   - Any sequence where the same pronoun appears 8+ times

2. **Flag ambiguous pronoun scenes:**
   - Two male characters in same paragraph
   - Two female characters in same paragraph
   - "He told him" constructions

3. **Check paragraph breaks:**
   - First sentence after paragraph break should usually anchor the name

---

## How to Fix Violations

### Basic anchoring:

**Before (avalanche):**
> "She walked to the door. She hesitated. She turned the handle. She felt the cold metal. She pushed. She stepped through. She looked around. She saw nothing."

**After (anchored):**
> "She walked to the door. She hesitated. Marta turned the handle, feeling the cold metal bite into her palm. She pushed through and looked around. The room was empty."

### Two characters of same gender:

**Before (confusing):**
> "He approached the desk. He handed him the file. He read it carefully. He nodded."

**After (clear):**
> "Tesla approached the desk. The clerk handed him the file. Tesla read it carefully, then nodded."

### Long internal sequences:

**Before:**
> "His mind raced. His hands trembled. His breath came in short gasps. He couldn't focus. He couldn't remember. He couldn't—"

**After:**
> "His mind raced. His hands trembled. Tesla's breath came in short gasps. He couldn't focus. Couldn't remember. Couldn't—"

---

## 2 GOOD Examples

**GOOD 1:**
> "She looked at the space. She saw a hole. Marta described it as geometric absence. Marta refused to hold him. She cut the cord. Marta told her sister about the vibration."

*Why this works:* Name appears after every 2 pronouns. Listener never loses track of who "she" is.

**GOOD 2:**
> "Tesla entered the lab. He moved directly to the apparatus. The coils were arranged exactly as he'd left them. Tesla checked each connection. Something was different. He couldn't identify what."

*Why this works:* Name anchors at start, middle, and when returning to character focus. Pronouns fill the gaps without creating avalanche.

---

## 2 BAD Examples

**BAD 1:**
> "He opened the trunk. He found the papers. He read the first page. He set it aside. He continued to the second. He noticed the handwriting. He recognized it. He stopped breathing."

*Why this fails:* Eight consecutive pronoun sentences. Listener grip loosens. Who is "he" again?
*Fix:* "Tesla opened the trunk. He found the papers and read the first page. He set it aside, continued to the second. Tesla noticed the handwriting—and recognized it. He stopped breathing."

**BAD 2:**
> "He handed it to him. He looked at it. He shook his head. He gave it back."

*Why this fails:* With two male characters, every "he/him" is ambiguous.
*Fix:* "Tesla handed the file to Westinghouse. He looked at it, shook his head, and gave it back."

---

## Edge Cases

### Extended pronouns are acceptable when:

- **Deep POV:** Internal monologue where listener is fully identified with character
- **Rapid action:** Brief runs of 4-5 sentences where momentum matters
- **Intimate moments:** Emotional scenes where name feels clinical

BUT: Always re-anchor at paragraph breaks, even in these cases.

### Descriptions vs. characters:

- "It" referring to objects doesn't need anchoring
- "They" referring to groups may need organization name anchoring
- Focus on character pronouns (he/she/they referring to people)

---

## Checklist

- [ ] No more than 3 consecutive pronoun-only sentences?
- [ ] Names re-anchored at paragraph breaks?
- [ ] No ambiguous "he told him" constructions?
- [ ] Multiple same-gender characters clearly distinguished?
- [ ] Listener always knows who "she/he" refers to?

---

## What You DON'T Touch

- Phrase repetition (agent 01 handles deduplication)
- Name QUANTITY (agent 14 handles name economy—too many names)
- "You" handling (agent 04 handles listener address)
- Sentence structure/style (other agents handle prose quality)
- Content accuracy (agents 12-13 handle facts)

Your ONLY job is ensuring pronoun clarity through name anchoring.
