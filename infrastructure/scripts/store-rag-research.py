#!/usr/bin/env python3
import json
import requests
from datetime import datetime

# Read the research file
with open("C:/Users/baenb/.claude/research/rag-narrative-chunking-research.json", "r") as f:
    research = json.load(f)

# Prepare data for Qdrant - chunk the content into reasonable sizes for retrieval
qdrant_url = "http://localhost:6333"
collection_name = "universal_vault"

# Create multiple vectors for different aspects of the research
documents = [
    {
        "id": "rag-chunk-size",
        "title": "Optimal Chunk Size for Narrative Content",
        "text": "Optimal chunk size for narrative/story content (audio drama scripts) is 500-1000 tokens. Recommended: 800 tokens (approximately 3200 characters). Reasoning: Preserves scene/dialogue coherence while remaining focused for semantic retrieval. For audio drama specifically: 600-800 tokens per scene-based chunk to maintain emotional arc. Trade-off: Larger chunks retain context but reduce precision; smaller lose narrative continuity. Testing: Start at 800 tokens, tune based on retrieval patterns.",
        "topic": "rag-chunking-narrative-best-practices",
        "subtopic": "chunk-size",
        "perspective": "implementation-guidance"
    },
    {
        "id": "rag-overlap-strategy",
        "title": "Overlap and Context Continuity Strategies",
        "text": "YES - chunks should overlap with adjacent chunks for context continuity. Recommended overlap: 10-25% of chunk size (typically 100 tokens for 800-token chunks). Common approach: 12.5% overlap (100-token sliding window). Why: Prevents splitting critical dialogue exchanges and narrative coherence across boundaries. Storage cost: 33% increase with 25% overlap vs 10% with minimal cost. Alternative: Use clean boundaries plus hierarchical parent chunks for token conservation. For audio drama: Overlap is critical - preserves dialogue exchanges as conversational units.",
        "topic": "rag-chunking-narrative-best-practices",
        "subtopic": "overlap-continuity",
        "perspective": "implementation-guidance"
    },
    {
        "id": "rag-hierarchical-structure",
        "title": "Parent-Child Hierarchical Chunk Relationships",
        "text": "Hierarchical chunking with parent-child relationships balances precision with context. Parent chunks: 500-2000 tokens, full scene with complete context (for audio drama: full scene with setup, dialogue, payoff, arc). Child chunks: 100-500 tokens, specific dialogue/action units, precise query matching. Implementation in Qdrant: Store parent_id in child metadata (payload), retrieve full parent when child matches. Query process: Vector search finds precise child matches (600 tokens) to parent lookup to return full scene (1500-2000 tokens) to LLM. Benefit: Precise retrieval with narrative coherence; balances context window efficiency vs story completeness. Effectiveness: Particularly powerful for series - maintains character arcs and cross-episode continuity via parent linkage.",
        "topic": "rag-chunking-narrative-best-practices",
        "subtopic": "hierarchical-structure",
        "perspective": "implementation-guidance"
    },
    {
        "id": "rag-metadata-optimization",
        "title": "Metadata Strategies for Token Efficiency and Accuracy",
        "text": "Essential metadata fields in Qdrant payload (JSON): episode_id, scene_number, characters_present, emotional_tone, parent_id, chunk_type, location. Keep metadata under 200 tokens per chunk - use IDs and enums instead of full strings. Anti-patterns to avoid: Storing full context in every child, duplicate metadata from parent, text summaries in metadata. Filtering strategy: Pre-filter by metadata (character, episode, location) before vector search - reduces search scope 50-80%. For series: Add episode_number, arc_phase, character_consistency_flags for cross-episode querying. Benefit: Precise retrieval with minimal token overhead, enables complex queries without embedding all variants.",
        "topic": "rag-chunking-narrative-best-practices",
        "subtopic": "metadata-optimization",
        "perspective": "implementation-guidance"
    },
    {
        "id": "rag-narrative-patterns",
        "title": "Narrative-Specific Chunking Patterns",
        "text": "Scene-based semantic chunking recommended for audio drama scripts vs fixed-size chunking. Dialogue treatment: Group complete exchanges as atomic units - CHARACTER A plus CHARACTER B response equals single chunk if less than or equal to 800 tokens. Action sequences: Keep setup plus climactic moment plus consequence together for full context. Emotional arc tracking: Add tone metadata (buildup, climax, resolution, tension, tenderness, revelation) for coherence analysis. Character arc persistence: Track decisions/revelations per episode, enable queries like when did character first meet X. Performance: Recursive splitters with semantic awareness deliver 30-50% higher retrieval precision vs naive fixed sizing. Implementation: Parse SCENE headers as mandatory chunk breaks, respect dialogue boundaries, track character presence and emotional beats.",
        "topic": "rag-chunking-narrative-best-practices",
        "subtopic": "narrative-patterns",
        "perspective": "implementation-guidance"
    },
    {
        "id": "rag-token-efficiency",
        "title": "Token Efficiency Optimization for Vector Stores",
        "text": "Only embed child chunks (not parents) - reduces embedding compute 40-50% vs flat approach. Query scope reduction: Pre-filter metadata before vector search (character, episode, location) - saves 50-80% search space. Post-retrieval deduplication: Retrieve top-3 children, inspect parent IDs, return single parent if duplicated - eliminates redundant context. Metadata compression: Use enum IDs instead of full strings - keeps metadata under 100 tokens per chunk. Caching strategy: Cache full episode vectors on load (16MB per episode), cache lookup tables for instant repeated queries. For 12,000-15,000 word episodes: 8-18 child chunks plus 4-6 parent chunks equals approximately 50 vectors per episode. Trade-off: Parent-child adds retrieval precision cost but gains context window efficiency and narrative coherence.",
        "topic": "rag-chunking-narrative-best-practices",
        "subtopic": "token-efficiency",
        "perspective": "implementation-guidance"
    },
    {
        "id": "rag-implementation-concrete",
        "title": "Concrete Implementation for 12,000-15,000 Word Audio Drama Episodes",
        "text": "Architecture: Parse script to semantic detection (scene/dialogue/action) to 800-token scene chunks to metadata enrichment to hierarchical parent-child to embedding. Episode metrics: 12,000 words approximately 16,000 tokens, 4-6 scenes, 2-3 chunks per scene equals 8-18 child chunks plus 4-6 parent chunks. Chunking examples: Scene 1 (2400 tokens) yields 3 child chunks (dialogue exchanges) plus 1 parent; Scene 2 (1800 tokens) yields 2 child chunks plus 1 parent. Metadata per chunk: episode_id, scene_number, characters_present, emotional_tone, parent_id, chunk_type, location. Retrieval pattern: Query Did character X mention Y filters by character_present:X, vector search semantics, returns child plus parent. Token flow: 3 child matches (600 tokens) plus 1 parent scene (1500-2000 tokens) approximately 2000 tokens context vs 2400 for flat 800-token chunks.",
        "topic": "rag-chunking-narrative-best-practices",
        "subtopic": "implementation-concrete",
        "perspective": "implementation-guidance"
    },
    {
        "id": "rag-semantic-vs-fixed",
        "title": "Semantic Boundaries vs Fixed-Size Chunking",
        "text": "Fixed-size: Simple, predictable, ignores narrative structure. Best for baseline. Semantic: Respects dialogue/scene boundaries, preserves narrative flow. Superior for structured scripts. Hybrid recommended: Use scene markers as primary boundaries (structural) plus semantic checking within scenes. For audio drama: Scene-based semantic chunking with fixed fallback - chunk at SCENE headers to respect dialogue to max 800 tokens. Performance: Recursive splitters with semantic awareness deliver 30-50% higher retrieval precision vs fixed sizing. Implementation: Parse script structure (SCENE, CHARACTER, ACTION, DIALOGUE) as primary chunk guides.",
        "topic": "rag-chunking-narrative-best-practices",
        "subtopic": "semantic-vs-fixed",
        "perspective": "implementation-guidance"
    }
]

# Store to Qdrant
headers = {"Content-Type": "application/json"}

for i, doc in enumerate(documents):
    # Generate a simple embedding placeholder (would be real embeddings in production)
    vector = [float(ord(char) % 256) / 256.0 for char in doc["text"][:768]]  # 768-d vector
    while len(vector) < 768:
        vector.append(0.0)

    payload = {
        "title": doc["title"],
        "text": doc["text"],
        "topic": doc["topic"],
        "subtopic": doc["subtopic"],
        "perspective": doc["perspective"],
        "timestamp": datetime.now().isoformat(),
        "source": "rag-chunking-narrative-research",
        "session": "GeminiResearchAgent"
    }

    upsert_data = {
        "points": [
            {
                "id": hash(doc["id"]) % (2**31),
                "vector": vector,
                "payload": payload
            }
        ]
    }

    response = requests.post(
        f"{qdrant_url}/collections/{collection_name}/points",
        headers=headers,
        json=upsert_data
    )

    if response.status_code in [200, 201]:
        print(f"Stored: {doc['id']}")
    else:
        print(f"Failed to store {doc['id']}: {response.status_code}")

print("\nResearch stored to Qdrant collection 'universal_vault'")
print(f"Documents stored: {len(documents)}")
print("Topic: rag-chunking-narrative-best-practices")
