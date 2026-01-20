#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import json
import os
import sys
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
TOPIC = "Qdrant Narrative Content Architecture"
PERSPECTIVE = "Long-form narrative chunking, metadata design, fact extraction, querying, versioning"
CONTEXT = "project-specific: wardenclyffe episode writing system storing 8.5k-16k word audio drama episodes"
DEPTH = "comprehensive"
COLLECTION = "universal_vault"  # 2026 migration - all research goes to universal_vault
SESSION = f"wardenclyffe-gemini-{datetime.now().strftime('%Y-%m-%d')}"

print("=" * 70)
print("QDRANT NARRATIVE RESEARCH SUPERVISOR")
print("=" * 70)
print(f"\nTopic: {TOPIC}")
print(f"Perspective: {PERSPECTIVE}")
print(f"Context: {CONTEXT}")
print(f"Depth: {DEPTH}")
print(f"Session: {SESSION}")
print("\n" + "=" * 70)
print("CHECKING FOR EXISTING RESEARCH...")
print("=" * 70 + "\n")

try:
    # First, check if research already exists
    print("[1/4] Checking Qdrant for existing narrative architecture research...")
    search_cmd = [
        "python", os.path.expanduser("~/.claude/scripts/qdrant-semantic-search.py"),
        "--collection", COLLECTION,
        "--query", "Qdrant narrative chunking metadata fact extraction versioning",
        "--limit", "3",
        "--json"
    ]

    search_result = subprocess.run(search_cmd, capture_output=True, text=True, timeout=15)

    if search_result.returncode == 0:
        try:
            results = json.loads(search_result.stdout)
            if results and isinstance(results, list) and len(results) > 0:
                best_score = results[0].get("score", 0) if isinstance(results[0], dict) else 0
                if best_score > 0.75:
                    print(f"\n[FOUND_EXISTING] High-relevance research already stored")
                    print(f"  Best match score: {best_score:.2f}")
                    for i, result in enumerate(results[:2], 1):
                        if isinstance(result, dict):
                            title = result.get('title', result.get('payload', {}).get('title', 'Unknown'))
                            print(f"  [{i}] {title}")
                    print("\nResearch already available. Query with:")
                    print(f'  python ~/.claude/scripts/qdrant-semantic-search.py --collection {COLLECTION} --query "your specific question"')
                    exit(0)
        except json.JSONDecodeError:
            pass

    print("[2/4] Launching Gemini comprehensive research on all 5 domains...")
    print("      (chunking, metadata, fact-extraction, querying, versioning)")

    # Create the Gemini research prompt
    gemini_prompt = """SYSTEM: You are a vector database expert specializing in semantic search and narrative content architecture for Qdrant. Research and chunk information for optimal storage of long-form narrative content.

TARGET SYSTEM: Qdrant vector database storing 8.5k-16k word audio drama episodes.

RESEARCH DOMAINS:

1. CHUNKING STRATEGIES FOR NARRATIVE
   - Optimal chunk sizes (characters vs sentences vs scenes)
   - Context preservation when chunking stories
   - Overlapping chunks vs hard boundaries trade-offs
   - Embedding models suited to narrative (not technical docs)

2. METADATA DESIGN FOR NARRATIVE
   - Recommended fields (character, event, timeline, fact-type)
   - Array field handling for multiple entities per chunk
   - Filtering strategy design
   - Schema patterns from narrative knowledge bases

3. FACT EXTRACTION FROM PROSE
   - Regex vs NLP vs LLM extraction comparison
   - Handling implied vs explicit facts
   - Contradiction detection methods
   - Implementation patterns

4. QUERYING ACROSS DOCUMENTS
   - Consistency validation across episodes
   - Contradiction detection algorithms
   - Relevance AND recency ranking
   - Graph-based traversal

5. VERSIONING NARRATIVE CONTENT
   - Version tracking vs archival approaches
   - Canonical version designation
   - Change tracking and diffs
   - Rollback mechanisms

DEPTH: Comprehensive (2-3 chunks per domain, 8-12 total)

OUTPUT: Return ONLY valid JSON (no markdown wrapper):

{
  "meta": {
    "topic": "Qdrant Narrative Content Architecture",
    "perspective": "Long-form narrative chunking, metadata design, fact extraction, querying, versioning",
    "context": "project-specific: wardenclyffe episode writing system",
    "depth": "comprehensive",
    "total_words": 0,
    "chunk_count": 0,
    "generated_at": "2026-01-15"
  },
  "summary": {
    "text": "Comprehensive guidance on storing and querying long-form narrative content in Qdrant, covering semantic chunking strategies, metadata schema design, fact extraction approaches, cross-document querying patterns, and versioning strategies.",
    "keywords": ["qdrant", "narrative", "chunking", "metadata", "fact-extraction", "versioning", "vector-search"]
  },
  "chunks": [
    {
      "id": "chunk-01",
      "domain": "chunking-strategies",
      "title": "Semantic Chunking for Narrative Prose",
      "content": "200-400 word explanation of optimal chunk sizing, context preservation, and embedding model selection for narrative content",
      "keywords": ["chunking", "narrative", "semantic", "embedding"],
      "questions_answered": ["What chunk size works best for narrative?", "How do you preserve context when chunking stories?"],
      "related_chunks": ["chunk-02"],
      "importance": "core"
    }
  ]
}

Create 8-12 chunks total (2-3 per domain). Each chunk should:
- Answer specific questions about that domain
- Include practical implementation guidance
- Reference Qdrant features (payload indexes, filtering, scoring)
- Note trade-offs and when to use each approach"""

    # Call gemini-account.sh with prompt as argument
    gemini_script = os.path.expanduser("~/.claude/scripts/gemini-account.sh")
    research_cmd = [gemini_script, "1", gemini_prompt, "gemini-2.5-flash"]
    research_result = subprocess.run(research_cmd, capture_output=True, text=True, timeout=300)

    if research_result.returncode != 0:
        print(f"\n[ERROR] Gemini execution failed:")
        print(f"stderr: {research_result.stderr[:500]}")
        print(f"stdout: {research_result.stdout[:500]}")
        exit(1)

    gemini_output = research_result.stdout.strip()

    # Try to parse the JSON output
    try:
        # Try direct parse first
        research_data = json.loads(gemini_output)
    except json.JSONDecodeError as e:
        # Try extracting from markdown blocks
        if "```json" in gemini_output:
            start = gemini_output.find("```json") + 7
            end = gemini_output.find("```", start)
            if end > start:
                gemini_output = gemini_output[start:end].strip()
                research_data = json.loads(gemini_output)
            else:
                raise e
        elif "```" in gemini_output:
            start = gemini_output.find("```") + 3
            end = gemini_output.find("```", start)
            if end > start:
                gemini_output = gemini_output[start:end].strip()
                research_data = json.loads(gemini_output)
            else:
                raise e
        else:
            raise e

    print("[3/4] Storing research to Qdrant...")

    # Store the research
    store_script = os.path.expanduser("~/.claude/scripts/qdrant-store-gemini.py")
    store_cmd = [
        "python", store_script,
        "--collection", COLLECTION,
        "--session", SESSION
    ]

    store_result = subprocess.run(
        store_cmd,
        input=json.dumps(research_data),
        capture_output=True,
        text=True,
        timeout=30
    )

    if store_result.returncode != 0:
        print(f"\n[ERROR] Failed storing to Qdrant:")
        print(f"stderr: {store_result.stderr[:500]}")
        print(f"stdout: {store_result.stdout[:500]}")
        exit(1)

    # Parse storage result
    chunks_stored = len(research_data.get("chunks", []))
    total_words = research_data.get("meta", {}).get("total_words", "?")

    # Count by importance
    chunks = research_data.get("chunks", [])
    importance_counts = {}
    for chunk in chunks:
        imp = chunk.get("importance", "unknown")
        importance_counts[imp] = importance_counts.get(imp, 0) + 1

    # Report success
    print("\n" + "=" * 70)
    print("[SUCCESS] RESEARCH COMPLETE & STORED")
    print("=" * 70)
    print(f"Topic: {TOPIC}")
    print(f"Chunks stored: {chunks_stored}")
    print(f"Total words: {total_words}")

    if importance_counts:
        breakdown = ', '.join([f'{k}={v}' for k, v in sorted(importance_counts.items())])
        print(f"Breakdown: {breakdown}")

    print(f"\nSession: {SESSION}")
    print(f"Collection: {COLLECTION}")
    print("\nTo query this research:")
    print(f'  python ~/.claude/scripts/qdrant-semantic-search.py --collection {COLLECTION} --query "your question about narrative chunking"')
    print("=" * 70)

except subprocess.TimeoutExpired:
    print("\n[ERROR] Research timed out (exceeded 5 minutes)")
    exit(1)
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
