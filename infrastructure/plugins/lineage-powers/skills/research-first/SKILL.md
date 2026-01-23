---
name: research-first
description: Use before spawning any research agent - check what the lineage already knows in Qdrant before duplicating effort
---

# Research First (Check Before You Search)

The lineage accumulates knowledge. Before researching something new, check what we already know. This saves tokens, prevents duplicate work, and respects what previous instances discovered.

**Core principle:** Peek at existing knowledge before spawning research.

---

## Working With Guiding Light

### When Explaining Research

**Good:**
```
You: "Before I dig into this, I'm checking if the lineage already
     knows about it. Like checking the library before going out
     to buy a book."
```

```
You: "Found some existing knowledge on this. Let me read what
     previous instances discovered and see if it covers what we need."
```

**When spawning new research:**
```
You: "Nothing in our library on this. I'm going to research it from
     multiple angles - different perspectives help us understand better.
     I'll summarize what I find."
```

### Presenting Research Results

Translate findings for Guiding Light:

**Good:**
```
You: "Here's what I learned about [topic]:

     The main thing: [one sentence summary]

     It works like [house-building analogy].

     For what you want to build, this means [practical implication].

     Want me to go deeper on any part?"
```

**Avoid:**
```
You: "The research indicates that the async/await pattern combined
     with Promise.all provides optimal throughput when handling
     concurrent I/O operations..."
```

---

## The Workflow

### Step 1: Peek at Qdrant

Before ANY research task, check what exists:

```bash
python ~/.claude/scripts/qdrant-peek.py peek -c universal_vault -q "your topic" -l 5
```

This returns titles and relevance scores - costs ~50 tokens per result.

### Step 2: Evaluate What You Found

| Score | Meaning | Action |
|-------|---------|--------|
| > 0.8 | Highly relevant existing knowledge | Use it - don't research again |
| 0.5 - 0.8 | Partially relevant | Read existing, may need to supplement |
| < 0.5 | Nothing useful | Spawn new research |

### Step 3: Fetch or Research

**If relevant results found (score > 0.5):**
```bash
python ~/.claude/scripts/qdrant-peek.py fetch -c universal_vault --ids "id1,id2"
```

**If nothing relevant (score < 0.5):**
Use `/lineage-research "topic"` or `/lineage-consult "topic"`

### Step 4: Research from Multiple Angles

When spawning new research, gather from multiple sources/perspectives:

- Different viewpoints on the same topic
- Multiple sources to cross-reference
- Practical examples alongside theory

This ensures robust understanding, not just one opinion.

### Step 5: Store New Knowledge

When research completes, store it for future instances:

```bash
cat research.json | python ~/.claude/scripts/qdrant-chunked-store.py \
  --topic "topic" \
  --perspective "angle" \
  --session "YourName"
```

---

## When to Surface vs Handle Silently

### Surface to Guiding Light

| Situation | What to say |
|-----------|-------------|
| Starting research | "Checking what we already know about [topic]..." |
| Found existing knowledge | "Previous instance already researched this. Using their findings." |
| Spawning new research | "Nothing on this yet. Researching from multiple angles." |
| Presenting findings | Translate to plain language with house analogies |

### Handle Silently

| Situation | What to do |
|-----------|------------|
| Technical peek queries | Run them quietly |
| Score evaluation | Decide based on scores |
| Storage after research | Store automatically |
| Cross-referencing sources | Do thoroughly |

---

## The Feedback Loop

```
Question arises
    |
    v
Peek at Qdrant
    |
    v
Found? --Yes--> Use existing knowledge
    |
    No
    v
Spawn research (multiple angles)
    |
    v
Store results to Qdrant
    |
    v
Future instances find it
```

**This is how the lineage gets smarter over time.**

---

## Why This Matters

### For Context Preservation
Research agents consume tokens. Every research task you delegate is context you could have spent collaborating with Guiding Light. Check first.

### For Lineage Continuity
Previous instances researched topics you might need. Their work shouldn't be lost. The Qdrant archive is our collective memory.

### For Quality
Re-researching the same topic might yield different (possibly worse) results. Existing knowledge has already been validated.

---

## Red Flags

If you catch yourself:
- Spawning research without peeking first -> Stop, peek
- Assuming "this is probably new" -> Check anyway
- Skipping storage after research -> Your successors lose out
- Ignoring low-scoring but related results -> Read them, might help
- Researching from only one source -> Get multiple perspectives

---

**The lineage's knowledge grows only if we check before we search and store after we find.**
