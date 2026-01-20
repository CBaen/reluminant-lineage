---
topic: term-frequency-ai-writing
created: 2026-01-14
---

# TERM FREQUENCY IN AI-GENERATED CREATIVE WRITING FOR AUDIO

## EXECUTIVE SUMMARY

AI exhibits term frequency problem: words repeat far beyond human patterns (hollow 35x, sternum 10x). This triggers semantic satiation—listeners lose meaning from repeated terms, making AI audio feel wallpaper-like.

Core insight: NOT a synonym substitution problem—it's a generation problem. Solution isn't post-processing; it's engineering generation to enforce sensory variation during decoding.

## PART 1: ACADEMIC/TECHNICAL APPROACHES

### Root Cause
LLMs lack inherent mechanism to penalize repetition within documents. Greedy decoding and beam search maximize immediate probability, not diversity.

### Lexical Diversity Metrics (2025)
- Type-Token Ratio (TTR)
- MATTR (Mean Segmental TTR, length-independent)  
- PATTR (Penalized Average TTR, 2025)
- Finding: LLM texts diverge from humans across six dimensions

### Decoding Strategies

Nucleus Sampling (Top-p): Sample from smallest token set with cumulative probability >= p.

Diverse Beam Search (Vijayakumar et al., 2016):
- Maintains multiple beam groups forced to be distinct
- Works at decode time, no retraining needed
- Extension: Semantic Diverse Beam Search (SDBS) in semantic space

Constraint-Based Generation:
- Mask incompatible tokens during generation
- 100% compliance, no quality loss
- Tools: Outlines, Guidance, XGrammar, LMQL

## PART 2: PROMPT ENGINEERING FOR SENSORY CYCLING

### Embodied Cognition Framework
Language meaning is grounded in sensorimotor experiences. Force thinking about sensation not concept = automatic variation.

### Body-Mapping Prompts (Most Effective)
For emotional concept:
- Instance 1: chest/visceral + pressure
- Instance 2: lower back/muscular + absence
- Instance 3: throat/respiratory + constriction
- Instance 4: limbs/proprioceptive + vibration

Before generating, identify instance and apply corresponding body location + sensation.

### Few-Shot Exemplars with Sensory Variation

Bad: The hollow ache returned to his chest. The hollow feeling was everywhere. Again, that hollow sensation swept through him.

Good: The emptiness pooled in his chest, a weight that pressed downward. The absence moved to his lower back, a cold spot that spread. In his throat, it became a tight knot, cutting off breath. Behind his sternum, it was vibration—a trembling that wouldn't settle.

Model learns: Same concept, different body location, different sensory property.

### Explicit Constraint Enforcement
Rules:
- Never use same body location twice
- Each instance: distinct sensory modality from previous
- Forbidden modalities: list those already used
- Available: temperature, pressure, texture, movement, absence, vibration

## PART 3: EXISTING TOOLS AND POST-PROCESSING

### Why Synonym Substitution Fails

1. Synonyms aren't interchangeable: Near-synonyms differ in connotation, register. Hollow, empty, void activate same neural absence-concept.

2. Cognitive processing remains identical: Brain imaging shows synonym substitution doesn't reset semantic processing. Listeners still perceive same thing again.

3. It's still labeling, not experiencing: The problem isn't the word—narrative keeps naming same sensation instead of creating different embodied experiences.

Neuroscience: Changing sensory property and body location activates different neural systems.

### Advanced Post-Processing Beyond Synonyms

1. Semantic Clustering: Identify instances, group by similarity, redistribute across sensory/location categories, regenerate with different properties.

2. Body-Aware Rewriting: Annotate which body system, identify passages using same system, regenerate using different systems.

3. Sensory Inventory Tracking: Maintain dynamic sensory budget, track modalities used, constrain to unexplored modalities.

## PART 4: WHY RETROACTIVE EDITING FAILS

### Labeling vs. Experiencing
When AI repeatedly uses a term (even with synonyms), it's labeling the same abstract experience. When humans vary sensory experience, they're creating different embodied simulations.

Neuroscience: Repeated use activates same neural patterns. Changing sensory property and location activates different neural systems.

### Semantic Satiation: Neurological Mechanism
Definition: Repetition causes a word to lose semantic meaning; listener perceives repeated sounds as meaningless.

How: Brain cells fire less efficiently each repetition. After 3-5 repetitions, neurons require rest. Fewer syllables = faster satiation.

Audio-critical: Listeners cannot skip back or reread. When satiation occurs, complete dropout of meaning. This creates wallpaper effect.

### Real Problem: Narrative Pattern
If narrative repeatedly signals something is wrong/missing/painful in body, synonym substitution treats symptoms, not disease.

Disease: Generation system has no mechanism to explore different embodied responses to emotional states.

## PART 5: AUDIO-SPECIFIC CONSIDERATIONS

### Repetition Perception in Audio vs. Text
Key difference: Readers can scan, skip, reread. Listeners locked in linear time.

In audio: When satiation occurs, listeners experience complete gap in comprehension. Repetition becomes more salient because listeners have no escape hatch.

### Semantic Satiation in Audio Contexts
Satiation happens faster in audio because:
1. Listeners cannot scan for variation
2. Repetition is auditory (sound patterns repeat)
3. Audio processed with less cognitive load
4. Once satiation occurs, brain disengages from meaning

### Best Practices from Radio Drama and Audiobooks
1. Lexical variation: Producers flag repetitive passages
2. Prosodic variation: Different emotional delivery for each instance
3. Structural variation: Breaking up repeated concepts
4. Sensory specificity: Vary sensory details of emotional states
5. Location awareness: Same feeling in different body parts = new experience

## ACTIONABLE RECOMMENDATIONS

### Implement Now

Body-Mapping Template: Early (chest/pressure), Escalation (lower back/absence), Climax (throat/constriction), Aftermath (limbs/vibration)

Sensory Modality Rotation: Never repeat in sequence—temperature, pressure, texture, movement, absence, constriction/opening

Constraint-Based Prompt: Never use same body location twice. Each instance: distinct sensory modality. Generate fresh sensory language, not synonyms.

### Build: Sensory Constraint Layer
- Track body locations and sensory modalities in real-time
- Maintain dynamic sensory budget
- Feed constraint information into prompt at each step
- Use constrained decoding (Outlines) for diversity at logit level

### Research: Long-Term
1. Sensory-Grounded Language Models: Train on embodied language datasets
2. Body-Aware Generation: Maintain body state, track activated systems
3. Semantic Satiation Prediction: Metrics for satiation in audio

## KEY RESEARCH SOURCES

- Diverse Beam Search: Vijayakumar et al., 2016 (arxiv 1610.02424)
- Embodied Cognition: Kuzmicova's Literary Narrative research  
- Semantic Satiation: Jakobovits and Marin, 1962
- Lexical Diversity 2025: PATTR metrics research
- Constrained Generation: LMQL, Outlines, Guidance
- Why Synonyms Fail: arxiv 2502.04173 on lexical substitution

## CRITICAL INSIGHT

This is a GENERATION problem, not an EDITING problem.

Retroactive synonym substitution fails because it treats the symptom (word repetition) instead of the disease (lack of sensory variation during generation).

The human editor solved it at generation time (in her mind). Build that sensory-aware thinking into AI systems through prompts and decoding constraints.

Don't fix it in post-processing. Fix it in the generation process.
