#!/usr/bin/env python3
"""
check-continuity.py - Detect contradictions between episodes

Compares new episode extractions against existing lore to find:
- Contradicting lore_fact entries
- Inconsistent character_state claims
- Timeline conflicts
- Relationship contradictions

Usage:
    python check-continuity.py --episode 3
    python check-continuity.py --episode 3 --strict  # Fail on any conflict
"""

import argparse
import json
import sys
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

# Config
QDRANT_URL = "http://localhost:6333"
COLLECTION = "tesla_mandela_effects"
SIMILARITY_THRESHOLD = 0.85  # High similarity might indicate contradiction

def get_client():
    return QdrantClient(url=QDRANT_URL)

def get_episode_extractions(client, episode_number: int, content_types: list = None) -> list:
    """Get extractions for a specific episode."""
    filters = [FieldCondition(key="episode_number", match=MatchValue(value=episode_number))]

    if content_types:
        # Get each type separately and combine
        all_results = []
        for ct in content_types:
            results = client.scroll(
                collection_name=COLLECTION,
                scroll_filter=Filter(must=[
                    FieldCondition(key="episode_number", match=MatchValue(value=episode_number)),
                    FieldCondition(key="content_type", match=MatchValue(value=ct))
                ]),
                limit=1000,
                with_payload=True
            )
            all_results.extend(results[0])
        return all_results

    results = client.scroll(
        collection_name=COLLECTION,
        scroll_filter=Filter(must=filters),
        limit=10000,
        with_payload=True
    )
    return results[0]

def get_prior_extractions(client, before_episode: int, content_types: list = None) -> list:
    """Get extractions from all episodes before the specified one."""
    all_results = []

    for ep in range(1, before_episode):
        results = get_episode_extractions(client, ep, content_types)
        all_results.extend(results)

    return all_results

def get_embedding(text: str) -> list[float]:
    """Get embedding from Ollama."""
    import subprocess

    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/embeddings",
             "-d", json.dumps({"model": "nomic-embed-text", "prompt": text[:2000]})],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("embedding", None)
    except Exception as e:
        print(f"[WARN] Embedding failed: {e}", file=sys.stderr)

    return None

def cosine_similarity(a: list, b: list) -> float:
    """Calculate cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)

def check_lore_conflicts(client, new_extractions: list, prior_extractions: list) -> list:
    """Check for contradicting lore_fact entries."""
    conflicts = []

    new_lore = [p for p in new_extractions if p.payload.get("content_type") == "lore_fact"]
    prior_lore = [p for p in prior_extractions if p.payload.get("content_type") == "lore_fact"]

    print(f"[INFO] Checking {len(new_lore)} new lore facts against {len(prior_lore)} prior facts...", file=sys.stderr)

    for new_item in new_lore:
        new_text = new_item.payload.get("text", "")
        new_embedding = get_embedding(new_text)

        if not new_embedding:
            continue

        for prior_item in prior_lore:
            prior_text = prior_item.payload.get("text", "")

            # Quick check: if texts are very similar, might be duplicate (OK) or contradiction (BAD)
            # Get prior embedding from stored vector if available
            prior_vector = prior_item.vector
            if isinstance(prior_vector, dict):
                prior_embedding = prior_vector.get("dense", [])
            else:
                prior_embedding = prior_vector if prior_vector else []

            if not prior_embedding:
                prior_embedding = get_embedding(prior_text)

            if prior_embedding:
                similarity = cosine_similarity(new_embedding, prior_embedding)

                # High similarity but different text = potential conflict
                if similarity > SIMILARITY_THRESHOLD:
                    # Check if texts are actually different
                    if new_text.lower().strip() != prior_text.lower().strip():
                        conflicts.append({
                            "type": "lore_conflict",
                            "severity": "high" if similarity > 0.92 else "medium",
                            "new_episode": new_item.payload.get("episode_number"),
                            "prior_episode": prior_item.payload.get("episode_number"),
                            "new_text": new_text,
                            "prior_text": prior_text,
                            "similarity": round(similarity, 3),
                            "reason": "Similar lore facts with different wording - may contradict"
                        })

    return conflicts

def check_character_conflicts(client, new_extractions: list, prior_extractions: list) -> list:
    """Check for inconsistent character_state claims."""
    conflicts = []

    new_states = [p for p in new_extractions if p.payload.get("content_type") == "character_state"]
    prior_states = [p for p in prior_extractions if p.payload.get("content_type") == "character_state"]

    print(f"[INFO] Checking {len(new_states)} new character states against {len(prior_states)} prior states...", file=sys.stderr)

    # Group by character
    def get_characters(payload):
        chars = payload.get("characters", [])
        if isinstance(chars, list):
            return chars
        return []

    for new_item in new_states:
        new_chars = get_characters(new_item.payload)
        new_text = new_item.payload.get("text", "")

        for prior_item in prior_states:
            prior_chars = get_characters(prior_item.payload)

            # Same character(s)?
            common_chars = set(new_chars) & set(prior_chars)
            if common_chars:
                prior_text = prior_item.payload.get("text", "")

                # Check for semantic similarity
                new_emb = get_embedding(new_text)
                prior_emb = get_embedding(prior_text)

                if new_emb and prior_emb:
                    similarity = cosine_similarity(new_emb, prior_emb)

                    # Similar topic about same character but different claim
                    if 0.7 < similarity < 0.95:
                        conflicts.append({
                            "type": "character_state_conflict",
                            "severity": "medium",
                            "characters": list(common_chars),
                            "new_episode": new_item.payload.get("episode_number"),
                            "prior_episode": prior_item.payload.get("episode_number"),
                            "new_text": new_text,
                            "prior_text": prior_text,
                            "similarity": round(similarity, 3),
                            "reason": "Similar claims about same character - verify consistency"
                        })

    return conflicts

def check_relationship_conflicts(client, new_extractions: list, prior_extractions: list) -> list:
    """Check for contradicting relationship claims."""
    conflicts = []

    new_rels = [p for p in new_extractions if p.payload.get("content_type") == "relationship"]
    prior_rels = [p for p in prior_extractions if p.payload.get("content_type") == "relationship"]

    print(f"[INFO] Checking {len(new_rels)} new relationships against {len(prior_rels)} prior relationships...", file=sys.stderr)

    for new_item in new_rels:
        new_a = new_item.payload.get("entity_a", "").lower()
        new_b = new_item.payload.get("entity_b", "").lower()
        new_type = new_item.payload.get("relationship_type", "")

        for prior_item in prior_rels:
            prior_a = prior_item.payload.get("entity_a", "").lower()
            prior_b = prior_item.payload.get("entity_b", "").lower()
            prior_type = prior_item.payload.get("relationship_type", "")

            # Same entities?
            same_pair = (
                (new_a == prior_a and new_b == prior_b) or
                (new_a == prior_b and new_b == prior_a)
            )

            if same_pair and new_type != prior_type:
                # Relationship type changed - might be evolution or conflict
                conflicts.append({
                    "type": "relationship_conflict",
                    "severity": "low",  # Relationships can evolve
                    "entities": [new_a, new_b],
                    "new_episode": new_item.payload.get("episode_number"),
                    "prior_episode": prior_item.payload.get("episode_number"),
                    "new_relationship": new_type,
                    "prior_relationship": prior_type,
                    "reason": "Relationship type changed - verify if intentional evolution"
                })

    return conflicts

def main():
    parser = argparse.ArgumentParser(description="Check continuity between episodes")
    parser.add_argument("--episode", "-e", type=int, required=True, help="Episode number to check")
    parser.add_argument("--strict", action="store_true", help="Exit with error if conflicts found")
    parser.add_argument("--output", "-o", help="Output file for report (JSON)")

    args = parser.parse_args()

    if args.episode < 2:
        print("[INFO] Episode 1 has nothing to compare against - no conflicts possible")
        return

    client = get_client()

    print(f"\n=== Continuity Check: Episode {args.episode} ===\n", file=sys.stderr)

    # Get extractions
    new_extractions = get_episode_extractions(client, args.episode)
    prior_extractions = get_prior_extractions(client, args.episode)

    print(f"[INFO] New episode has {len(new_extractions)} extractions", file=sys.stderr)
    print(f"[INFO] Prior episodes have {len(prior_extractions)} extractions", file=sys.stderr)

    # Run checks
    all_conflicts = []

    all_conflicts.extend(check_lore_conflicts(client, new_extractions, prior_extractions))
    all_conflicts.extend(check_character_conflicts(client, new_extractions, prior_extractions))
    all_conflicts.extend(check_relationship_conflicts(client, new_extractions, prior_extractions))

    # Report
    report = {
        "episode": args.episode,
        "timestamp": datetime.now().isoformat(),
        "new_extractions": len(new_extractions),
        "prior_extractions": len(prior_extractions),
        "conflicts_found": len(all_conflicts),
        "conflicts_by_severity": {
            "high": len([c for c in all_conflicts if c.get("severity") == "high"]),
            "medium": len([c for c in all_conflicts if c.get("severity") == "medium"]),
            "low": len([c for c in all_conflicts if c.get("severity") == "low"])
        },
        "conflicts": all_conflicts
    }

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n[OK] Report saved to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(report, indent=2))

    # Summary
    print(f"\n=== Summary ===", file=sys.stderr)
    print(f"Conflicts found: {len(all_conflicts)}", file=sys.stderr)
    print(f"  High severity: {report['conflicts_by_severity']['high']}", file=sys.stderr)
    print(f"  Medium severity: {report['conflicts_by_severity']['medium']}", file=sys.stderr)
    print(f"  Low severity: {report['conflicts_by_severity']['low']}", file=sys.stderr)

    if args.strict and report['conflicts_by_severity']['high'] > 0:
        print("\n[ERROR] High severity conflicts found - failing", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
