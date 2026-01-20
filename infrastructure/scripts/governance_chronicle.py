#!/usr/bin/env python3
"""
governance_chronicle.py - Comprehensive Governance Data Storage

Stores EVERYTHING each governance model does:
- All research from every agent
- All synthesizer proposals
- All votes, rankings, and eliminations
- All files created
- Complete narrative trail

Key Constraint: Each government can only review their own prior actions.

Collection: governance_chronicle
Point types: research, proposal, vote, round, decision, file
"""

import os
import sys
import json
import uuid
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

QDRANT_URL = "http://localhost:6333"
COLLECTION = "governance_chronicle"
EMBEDDING_DIM = 768

# Government ID mapping
GOVERNMENT_IDS = {
    "ultrathink-simple": "swift_path",
    "ultrathink-review": "council",
    "ultrathink-consensus": "parliament",
    "swift_path": "swift_path",
    "council": "council",
    "parliament": "parliament"
}


def get_government_id(variant: str) -> str:
    """Convert variant name to government_id."""
    return GOVERNMENT_IDS.get(variant, variant)


def get_ollama_embedding(text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
    """Get embedding from local Ollama."""
    try:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": model, "prompt": text[:8000]},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("embedding")
    except:
        pass
    return None


def get_hash_embedding(text: str) -> List[float]:
    """Deterministic hash-based fallback embedding."""
    hash_bytes = hashlib.sha256(text.encode()).digest()
    embedding = []
    for i in range(EMBEDDING_DIM):
        byte_idx = i % len(hash_bytes)
        embedding.append((hash_bytes[byte_idx] / 255.0) * 2 - 1)
    return embedding


def get_embedding(text: str) -> List[float]:
    """Get embedding with Ollama fallback to hash."""
    if not text or not text.strip():
        return get_hash_embedding("empty")
    embedding = get_ollama_embedding(text)
    if embedding:
        return embedding
    return get_hash_embedding(text)


def ensure_collection() -> bool:
    """Create collection if it doesn't exist."""
    try:
        response = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass

    try:
        response = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION}",
            json={
                "vectors": {"size": EMBEDDING_DIM, "distance": "Cosine"},
                "optimizers_config": {"indexing_threshold": 10000}
            },
            timeout=10
        )
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"[Chronicle] Collection creation failed: {e}", file=sys.stderr)
        return False


def generate_point_id() -> str:
    """Generate unique point ID."""
    return str(uuid.uuid4())


def store_point(point_id: str, vector: List[float], payload: Dict) -> bool:
    """Store a single point in Qdrant."""
    try:
        response = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION}/points",
            json={
                "points": [{
                    "id": point_id,
                    "vector": vector,
                    "payload": payload
                }]
            },
            timeout=30
        )
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"[Chronicle] Store failed: {e}", file=sys.stderr)
        return False


# ============================================================
# STORE FUNCTIONS - One per point type
# ============================================================

def store_research(
    government_id: str,
    cycle_num: int,
    agent_role: str,
    agent_name: str,
    agent_focus: str,
    question: str,
    analysis: str,
    raw_response: str,
    key_insights: str = "",
    recommendations: str = "",
    session_id: str = None
) -> Optional[str]:
    """Store individual agent research."""
    ensure_collection()

    point_id = generate_point_id()
    timestamp = datetime.now().isoformat()

    # Embed the analysis content
    embed_text = f"{agent_name} analyzing: {question}\n\n{analysis}"
    vector = get_embedding(embed_text)

    payload = {
        "type": "research",
        "government_id": get_government_id(government_id),
        "cycle_num": cycle_num,
        "cycle_id": f"{get_government_id(government_id)}-{cycle_num}",
        "session_id": session_id or f"{government_id}-{timestamp}",
        "timestamp": timestamp,

        # Agent identity
        "agent_role": agent_role,
        "agent_name": agent_name,
        "agent_focus": agent_focus,

        # Research content
        "question": question[:500] if question else "",
        "analysis": analysis,
        "key_insights": key_insights,
        "recommendations": recommendations,
        "raw_response": raw_response
    }

    if store_point(point_id, vector, payload):
        return point_id
    return None


def store_proposal(
    government_id: str,
    cycle_num: int,
    synthesizer_role: str,
    synthesizer_name: str,
    synthesizer_lens: str,
    title: str,
    decision: str,
    why: str,
    risk: str,
    file_path: str,
    action: str,
    content: str,
    raw_response: str,
    option_letter: str = None,
    based_on_research: List[str] = None
) -> Optional[str]:
    """Store synthesizer proposal."""
    ensure_collection()

    point_id = generate_point_id()
    timestamp = datetime.now().isoformat()

    # Embed the proposal
    embed_text = f"{title}\n\nDecision: {decision}\nRationale: {why}"
    vector = get_embedding(embed_text)

    payload = {
        "type": "proposal",
        "government_id": get_government_id(government_id),
        "cycle_num": cycle_num,
        "cycle_id": f"{get_government_id(government_id)}-{cycle_num}",
        "timestamp": timestamp,

        # Synthesizer identity
        "synthesizer_role": synthesizer_role,
        "synthesizer_name": synthesizer_name,
        "synthesizer_lens": synthesizer_lens,

        # Proposal content
        "title": title,
        "decision": decision,
        "why": why,
        "risk": risk,
        "file_path": file_path,
        "action": action,
        "content": content,
        "raw_response": raw_response,

        # Linkage
        "option_letter": option_letter,
        "based_on_research": based_on_research or []
    }

    if store_point(point_id, vector, payload):
        return point_id
    return None


def store_vote(
    government_id: str,
    cycle_num: int,
    voter_role: str,
    voter_name: str,
    raw_response: str,
    # For ranked choice (Parliament)
    rankings: List[str] = None,
    rank_1: str = None,
    rank_2: str = None,
    rank_3: str = None,
    rank_4: str = None,
    reject_all: bool = False,
    confidence: float = 0.5,
    reasons: Dict[str, str] = None,
    # For simple voting (Council)
    verdict: str = None,
    reason: str = None,
    suggestion: str = None,
    # Linkage
    voted_for_proposal: str = None
) -> Optional[str]:
    """Store individual vote."""
    ensure_collection()

    point_id = generate_point_id()
    timestamp = datetime.now().isoformat()

    # Embed the vote reasoning
    if reasons:
        reasons_text = "\n".join([f"{k}: {v}" for k, v in reasons.items()])
    else:
        reasons_text = reason or ""
    embed_text = f"{voter_name} votes: {reasons_text}"
    vector = get_embedding(embed_text)

    payload = {
        "type": "vote",
        "government_id": get_government_id(government_id),
        "cycle_num": cycle_num,
        "cycle_id": f"{get_government_id(government_id)}-{cycle_num}",
        "timestamp": timestamp,

        # Voter identity
        "voter_role": voter_role,
        "voter_name": voter_name,

        # Ranked choice fields
        "rankings": rankings or [],
        "rank_1": rank_1,
        "rank_2": rank_2,
        "rank_3": rank_3,
        "rank_4": rank_4,
        "reject_all": reject_all,
        "confidence": confidence,
        "reasons": reasons or {},

        # Simple vote fields
        "verdict": verdict,
        "reason": reason,
        "suggestion": suggestion,

        # Raw and linkage
        "raw_response": raw_response,
        "voted_for_proposal": voted_for_proposal
    }

    if store_point(point_id, vector, payload):
        return point_id
    return None


def store_round(
    government_id: str,
    cycle_num: int,
    round_number: int,
    active_options: List[str],
    first_choice_counts: Dict[str, int],
    eliminated: str = None,
    eliminated_reason: str = None,
    winner: str = None
) -> Optional[str]:
    """Store ranked choice elimination round."""
    ensure_collection()

    point_id = generate_point_id()
    timestamp = datetime.now().isoformat()

    # Use hash embedding since rounds don't have semantic content
    embed_text = f"Round {round_number}: {json.dumps(first_choice_counts)}"
    vector = get_hash_embedding(embed_text)

    payload = {
        "type": "round",
        "government_id": get_government_id(government_id),
        "cycle_num": cycle_num,
        "cycle_id": f"{get_government_id(government_id)}-{cycle_num}",
        "timestamp": timestamp,

        # Round details
        "round_number": round_number,
        "active_options": active_options,
        "first_choice_counts": first_choice_counts,
        "eliminated": eliminated,
        "eliminated_reason": eliminated_reason or "Fewest first-choice votes",
        "winner": winner
    }

    if store_point(point_id, vector, payload):
        return point_id
    return None


def store_decision(
    government_id: str,
    cycle_num: int,
    question: str,
    winning_source: str,
    decision_text: str,
    risk: str,
    file_path: str,
    action_taken: bool,
    verification_passed: bool,
    # Outcome flags
    unanimous_rejection: bool = False,
    return_to_mirror: bool = False,
    parliament_proposed_own: bool = False,
    total_ranked_rounds: int = 0,
    # Linkage
    research_ids: List[str] = None,
    proposal_ids: List[str] = None,
    vote_ids: List[str] = None,
    round_ids: List[str] = None,
    file_id: str = None,
    winning_proposal_id: str = None
) -> Optional[str]:
    """Store cycle decision/outcome."""
    ensure_collection()

    point_id = generate_point_id()
    timestamp = datetime.now().isoformat()

    # Embed decision summary
    embed_text = f"Question: {question}\nDecision: {decision_text}\nSource: {winning_source}"
    vector = get_embedding(embed_text)

    payload = {
        "type": "decision",
        "government_id": get_government_id(government_id),
        "cycle_num": cycle_num,
        "cycle_id": f"{get_government_id(government_id)}-{cycle_num}",
        "timestamp": timestamp,

        # Decision content
        "question": question[:500] if question else "",
        "winning_proposal_id": winning_proposal_id,
        "winning_source": winning_source,
        "decision_text": decision_text,
        "risk": risk,

        # Outcome
        "unanimous_rejection": unanimous_rejection,
        "return_to_mirror": return_to_mirror,
        "parliament_proposed_own": parliament_proposed_own,
        "total_ranked_rounds": total_ranked_rounds,

        # Implementation outcome
        "file_path": file_path,
        "action_taken": action_taken,
        "verification_passed": verification_passed,

        # Linkage
        "research_ids": research_ids or [],
        "proposal_ids": proposal_ids or [],
        "vote_ids": vote_ids or [],
        "round_ids": round_ids or [],
        "file_id": file_id
    }

    if store_point(point_id, vector, payload):
        return point_id
    return None


def store_file(
    government_id: str,
    cycle_num: int,
    file_path: str,
    action: str,
    content: str,
    proposal_id: str = None,
    decision_id: str = None
) -> Optional[str]:
    """Store file content created."""
    ensure_collection()

    point_id = generate_point_id()
    timestamp = datetime.now().isoformat()

    # Embed file content
    vector = get_embedding(content[:4000] if content else "empty file")

    content_hash = hashlib.sha256(content.encode()).hexdigest() if content else ""
    line_count = len(content.split('\n')) if content else 0

    payload = {
        "type": "file",
        "government_id": get_government_id(government_id),
        "cycle_num": cycle_num,
        "cycle_id": f"{get_government_id(government_id)}-{cycle_num}",
        "timestamp": timestamp,

        # File details
        "file_path": file_path,
        "action": action,
        "content": content,
        "content_hash": content_hash,
        "line_count": line_count,

        # Linkage
        "proposal_id": proposal_id,
        "decision_id": decision_id
    }

    if store_point(point_id, vector, payload):
        return point_id
    return None


# ============================================================
# QUERY FUNCTIONS - Retrieve stored data
# ============================================================

def scroll_points(
    government_id: str,
    point_type: str = None,
    cycle_num: int = None,
    limit: int = 100,
    order_by: str = "timestamp"
) -> List[Dict]:
    """Scroll through points with filters."""
    must_conditions = [
        {"key": "government_id", "match": {"value": get_government_id(government_id)}}
    ]

    if point_type:
        must_conditions.append({"key": "type", "match": {"value": point_type}})

    if cycle_num is not None:
        must_conditions.append({"key": "cycle_num", "match": {"value": cycle_num}})

    try:
        response = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION}/points/scroll",
            json={
                "filter": {"must": must_conditions},
                "limit": limit,
                "with_payload": True,
                "with_vector": False
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            points = data.get("result", {}).get("points", [])
            # Sort by timestamp or specified field
            return sorted(points, key=lambda p: p.get("payload", {}).get(order_by, ""))

    except Exception as e:
        print(f"[Chronicle] Scroll failed: {e}", file=sys.stderr)

    return []


def get_cycle_narrative(government_id: str, cycle_num: int) -> Dict:
    """Reconstruct complete narrative of a cycle."""
    gov_id = get_government_id(government_id)

    # Get all points for this cycle
    research = scroll_points(gov_id, "research", cycle_num)
    proposals = scroll_points(gov_id, "proposal", cycle_num)
    votes = scroll_points(gov_id, "vote", cycle_num)
    rounds = scroll_points(gov_id, "round", cycle_num, order_by="round_number")
    decisions = scroll_points(gov_id, "decision", cycle_num)
    files = scroll_points(gov_id, "file", cycle_num)

    decision = decisions[0]["payload"] if decisions else {}

    return {
        "government_id": gov_id,
        "cycle_num": cycle_num,
        "chapter_1_mirror": {
            "question": decision.get("question", "")
        },
        "chapter_2_research": [p["payload"] for p in research],
        "chapter_3_synthesis": [p["payload"] for p in proposals],
        "chapter_4_voting": {
            "votes": [p["payload"] for p in votes],
            "rounds": [p["payload"] for p in rounds]
        },
        "chapter_5_decision": decision,
        "chapter_6_outcome": files[0]["payload"] if files else {}
    }


def get_research_history(
    government_id: str,
    agent_role: str = None,
    limit: int = 50
) -> List[Dict]:
    """Get research history for an agent."""
    gov_id = get_government_id(government_id)
    points = scroll_points(gov_id, "research", limit=limit)

    if agent_role:
        points = [p for p in points if p.get("payload", {}).get("agent_role") == agent_role]

    return [p["payload"] for p in points]


def get_proposal_history(
    government_id: str,
    synthesizer_role: str = None,
    limit: int = 50
) -> List[Dict]:
    """Get proposal history for a synthesizer."""
    gov_id = get_government_id(government_id)
    points = scroll_points(gov_id, "proposal", limit=limit)

    if synthesizer_role:
        points = [p for p in points if p.get("payload", {}).get("synthesizer_role") == synthesizer_role]

    return [p["payload"] for p in points]


def get_vote_patterns(
    government_id: str,
    voter_role: str = None,
    limit: int = 50
) -> List[Dict]:
    """Get voting patterns for an agent."""
    gov_id = get_government_id(government_id)
    points = scroll_points(gov_id, "vote", limit=limit)

    if voter_role:
        points = [p for p in points if p.get("payload", {}).get("voter_role") == voter_role]

    return [p["payload"] for p in points]


def search_decisions(
    government_id: str,
    query: str,
    limit: int = 10
) -> List[Dict]:
    """Semantic search across decisions."""
    gov_id = get_government_id(government_id)

    vector = get_embedding(query)

    try:
        response = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
            json={
                "vector": vector,
                "filter": {
                    "must": [
                        {"key": "government_id", "match": {"value": gov_id}},
                        {"key": "type", "match": {"value": "decision"}}
                    ]
                },
                "limit": limit,
                "with_payload": True
            },
            timeout=30
        )

        if response.status_code == 200:
            results = response.json().get("result", [])
            return [{"payload": r["payload"], "score": r["score"]} for r in results]

    except Exception as e:
        print(f"[Chronicle] Search failed: {e}", file=sys.stderr)

    return []


def format_narrative(narrative: Dict) -> str:
    """Format narrative as human-readable story."""
    gov = narrative.get("government_id", "unknown")
    cycle = narrative.get("cycle_num", "?")
    question = narrative.get("chapter_1_mirror", {}).get("question", "Unknown question")

    lines = [
        f"CYCLE {cycle}: {gov.upper()} addresses",
        f'"{question[:80]}..."',
        ""
    ]

    # Research
    research = narrative.get("chapter_2_research", [])
    if research:
        lines.append("THE AGENTS SPEAK:")
        for r in research:
            name = r.get("agent_name", r.get("agent_role", "Agent"))
            analysis = r.get("analysis", "")[:100]
            lines.append(f"- {name}: {analysis}...")
        lines.append("")

    # Proposals
    proposals = narrative.get("chapter_3_synthesis", [])
    if proposals:
        lines.append("PROPOSALS:")
        for p in proposals:
            letter = p.get("option_letter", "?")
            name = p.get("synthesizer_name", p.get("synthesizer_role", "Synth"))
            title = p.get("title", "Untitled")
            risk = p.get("risk", "?")
            lines.append(f"- Option {letter} ({name}): \"{title}\" - {risk} risk")
        lines.append("")

    # Voting
    voting = narrative.get("chapter_4_voting", {})
    votes = voting.get("votes", [])
    if votes:
        lines.append("VOTES:")
        for v in votes:
            name = v.get("voter_name", v.get("voter_role", "Voter"))
            if v.get("rankings"):
                rankings_str = " > ".join(v["rankings"])
                lines.append(f"- {name}: {rankings_str}")
            elif v.get("verdict"):
                lines.append(f"- {name}: {v['verdict']}")
        lines.append("")

    rounds = voting.get("rounds", [])
    if rounds:
        lines.append("ELIMINATION ROUNDS:")
        for r in rounds:
            rnum = r.get("round_number", "?")
            counts = r.get("first_choice_counts", {})
            counts_str = ", ".join([f"{k}={v}" for k, v in counts.items()])
            eliminated = r.get("eliminated")
            winner = r.get("winner")
            if winner:
                lines.append(f"- Round {rnum}: {counts_str} -> {winner} WINS")
            elif eliminated:
                lines.append(f"- Round {rnum}: {counts_str} -> {eliminated} eliminated")
        lines.append("")

    # Decision
    decision = narrative.get("chapter_5_decision", {})
    if decision:
        source = decision.get("winning_source", "unknown")
        decision_text = decision.get("decision_text", "No decision")[:100]
        lines.append("THE DECISION:")
        lines.append(f"Source: {source}")
        lines.append(f"Decision: {decision_text}...")

        if decision.get("action_taken"):
            file_path = decision.get("file_path", "unknown")
            verified = "PASSED" if decision.get("verification_passed") else "FAILED"
            lines.append(f"File: {file_path}")
            lines.append(f"Verification: {verified}")

    return "\n".join(lines)


# ============================================================
# CONVENIENCE FUNCTION - Store full cycle at once
# ============================================================

def store_full_cycle(
    government_id: str,
    cycle_num: int,
    cycle_data: Dict
) -> Dict[str, Any]:
    """
    Store all data from a complete cycle.

    Expects cycle_data with keys matching the governance variant:
    - For Parliament: quintet, triumvirate_proposals, ranked_votes, ranked_result, etc.
    - For Council: triad, proposal, reviews, final, etc.
    - For Swift Path: triad, synthesis, action_spec

    Returns dict of all generated UUIDs.
    """
    gov_id = get_government_id(government_id)
    session_id = f"{gov_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    result = {
        "research_ids": [],
        "proposal_ids": [],
        "vote_ids": [],
        "round_ids": [],
        "decision_id": None,
        "file_id": None
    }

    question = cycle_data.get("question", cycle_data.get("limitation", ""))

    # ===== PARLIAMENT (ultrathink-consensus) =====
    if gov_id == "parliament":
        # Add project path for imports
        parliament_path = Path.home() / "projects" / "ultrathink-consensus" / "core"
        if str(parliament_path) not in sys.path:
            sys.path.insert(0, str(parliament_path))
        try:
            from quintet import QUINTET_ROLES
            from triumvirate import TRIUMVIRATE_ROLES
        except ImportError:
            # Fallback role definitions
            QUINTET_ROLES = {
                "builder": {"name": "The Builder", "focus": "practical implementation"},
                "critic": {"name": "The Critic", "focus": "risks and gaps"},
                "seeker": {"name": "The Seeker", "focus": "unexplored possibilities"},
                "guardian": {"name": "The Guardian", "focus": "system safety"},
                "pragmatist": {"name": "The Pragmatist", "focus": "feasibility"}
            }
            TRIUMVIRATE_ROLES = {
                "architect": {"name": "The Architect", "lens": "practical/feasible"},
                "visionary": {"name": "The Visionary", "lens": "bold/innovative"},
                "steward": {"name": "The Steward", "lens": "safe/wise"}
            }

        # Store quintet research
        quintet = cycle_data.get("quintet", {})
        for role, content in quintet.items():
            if content and "ERROR" not in str(content):
                role_def = QUINTET_ROLES.get(role, {})
                pid = store_research(
                    government_id=gov_id,
                    cycle_num=cycle_num,
                    agent_role=role,
                    agent_name=role_def.get("name", role),
                    agent_focus=role_def.get("focus", ""),
                    question=question,
                    analysis=content,
                    raw_response=content,
                    session_id=session_id
                )
                if pid:
                    result["research_ids"].append(pid)

        # Store triumvirate proposals
        proposals = cycle_data.get("triumvirate_proposals", {})
        option_letters = {"architect": "A", "visionary": "B", "steward": "C", "collaborative": "D"}
        for role, proposal in proposals.items():
            if proposal:
                role_def = TRIUMVIRATE_ROLES.get(role, {})
                pid = store_proposal(
                    government_id=gov_id,
                    cycle_num=cycle_num,
                    synthesizer_role=role,
                    synthesizer_name=role_def.get("name", role),
                    synthesizer_lens=role_def.get("lens", ""),
                    title=proposal.get("title", ""),
                    decision=proposal.get("decision", ""),
                    why=proposal.get("why", ""),
                    risk=proposal.get("risk", ""),
                    file_path=proposal.get("file_path", ""),
                    action=proposal.get("action", ""),
                    content=proposal.get("content", ""),
                    raw_response=proposal.get("raw", ""),
                    option_letter=option_letters.get(role),
                    based_on_research=result["research_ids"]
                )
                if pid:
                    result["proposal_ids"].append(pid)

        # Store ranked votes
        ranked_votes = cycle_data.get("ranked_votes", {})
        for role, vote_data in ranked_votes.items():
            if vote_data:
                role_def = QUINTET_ROLES.get(role, {})
                vid = store_vote(
                    government_id=gov_id,
                    cycle_num=cycle_num,
                    voter_role=role,
                    voter_name=role_def.get("name", role),
                    raw_response=vote_data.get("raw", ""),
                    rankings=vote_data.get("rankings", []),
                    rank_1=vote_data.get("rank_1"),
                    rank_2=vote_data.get("rank_2"),
                    rank_3=vote_data.get("rank_3"),
                    rank_4=vote_data.get("rank_4"),
                    reject_all=vote_data.get("reject_all", False),
                    confidence=vote_data.get("confidence", 0.5),
                    reasons=vote_data.get("reasons", {})
                )
                if vid:
                    result["vote_ids"].append(vid)

        # Store elimination rounds
        ranked_result = cycle_data.get("ranked_result", {})
        rounds = ranked_result.get("rounds", [])
        # Handle rounds being either a list of round data or just a count
        if isinstance(rounds, list):
            for i, round_data in enumerate(rounds):
                rid = store_round(
                    government_id=gov_id,
                    cycle_num=cycle_num,
                    round_number=i + 1,
                    active_options=round_data.get("active_options", []),
                    first_choice_counts=round_data.get("first_choices", {}),
                    eliminated=round_data.get("eliminated"),
                    winner=round_data.get("winner")
                )
                if rid:
                    result["round_ids"].append(rid)

    # ===== COUNCIL (ultrathink-review) =====
    elif gov_id == "council":
        # Store triad research
        triad = cycle_data.get("triad", {})
        triad_roles = {
            "builder": {"name": "The Builder", "focus": "practical implementation"},
            "critic": {"name": "The Critic", "focus": "risk analysis"},
            "seeker": {"name": "The Seeker", "focus": "alternatives"}
        }
        for role, content in triad.items():
            if content and "ERROR" not in str(content):
                role_def = triad_roles.get(role, {})
                pid = store_research(
                    government_id=gov_id,
                    cycle_num=cycle_num,
                    agent_role=role,
                    agent_name=role_def.get("name", role),
                    agent_focus=role_def.get("focus", ""),
                    question=question,
                    analysis=content,
                    raw_response=content,
                    session_id=session_id
                )
                if pid:
                    result["research_ids"].append(pid)

        # Store proposal
        proposal = cycle_data.get("proposal", "")
        if proposal:
            pid = store_proposal(
                government_id=gov_id,
                cycle_num=cycle_num,
                synthesizer_role="synthesizer",
                synthesizer_name="The Synthesizer",
                synthesizer_lens="Integration of perspectives",
                title="Council Proposal",
                decision=cycle_data.get("action_spec", {}).get("decision", ""),
                why=cycle_data.get("action_spec", {}).get("why", ""),
                risk=cycle_data.get("action_spec", {}).get("risk", ""),
                file_path=cycle_data.get("action_spec", {}).get("file_path", ""),
                action=cycle_data.get("action_spec", {}).get("action", ""),
                content=cycle_data.get("action_spec", {}).get("content", ""),
                raw_response=proposal,
                based_on_research=result["research_ids"]
            )
            if pid:
                result["proposal_ids"].append(pid)

        # Store reviews (CRITICAL - currently 100% lost)
        reviews = cycle_data.get("reviews", {})
        for role, review_data in reviews.items():
            if review_data:
                role_def = triad_roles.get(role, {})
                vid = store_vote(
                    government_id=gov_id,
                    cycle_num=cycle_num,
                    voter_role=role,
                    voter_name=role_def.get("name", role),
                    raw_response=review_data.get("raw", ""),
                    verdict=review_data.get("verdict"),
                    reason=review_data.get("reason", ""),
                    suggestion=review_data.get("suggestion", "")
                )
                if vid:
                    result["vote_ids"].append(vid)

    # ===== SWIFT PATH (ultrathink-simple) =====
    elif gov_id == "swift_path":
        # Store triad research
        triad = cycle_data.get("triad", {})
        triad_roles = {
            "builder": {"name": "The Builder", "focus": "practical implementation"},
            "critic": {"name": "The Critic", "focus": "risk analysis"},
            "seeker": {"name": "The Seeker", "focus": "alternatives"}
        }
        for role, content in triad.items():
            if content and "ERROR" not in str(content):
                role_def = triad_roles.get(role, {})
                pid = store_research(
                    government_id=gov_id,
                    cycle_num=cycle_num,
                    agent_role=role,
                    agent_name=role_def.get("name", role),
                    agent_focus=role_def.get("focus", ""),
                    question=question,
                    analysis=content,
                    raw_response=content,
                    session_id=session_id
                )
                if pid:
                    result["research_ids"].append(pid)

        # Store synthesis as proposal
        synthesis = cycle_data.get("synthesis", "")
        action_spec = cycle_data.get("action_spec", {})
        if synthesis or action_spec:
            pid = store_proposal(
                government_id=gov_id,
                cycle_num=cycle_num,
                synthesizer_role="synthesizer",
                synthesizer_name="The Synthesizer",
                synthesizer_lens="Direct integration",
                title="Swift Path Synthesis",
                decision=action_spec.get("decision", ""),
                why=action_spec.get("why", ""),
                risk=action_spec.get("risk", ""),
                file_path=action_spec.get("file_path", ""),
                action=action_spec.get("action", ""),
                content=action_spec.get("content", ""),
                raw_response=synthesis,
                based_on_research=result["research_ids"]
            )
            if pid:
                result["proposal_ids"].append(pid)

    # ===== STORE DECISION (all variants) =====
    action_spec = cycle_data.get("action_spec", {})
    final_proposal = cycle_data.get("final_proposal", {})
    ranked_result = cycle_data.get("ranked_result", {})

    decision_id = store_decision(
        government_id=gov_id,
        cycle_num=cycle_num,
        question=question,
        winning_source=final_proposal.get("source", action_spec.get("synthesizer", "synthesizer")),
        decision_text=action_spec.get("decision", ""),
        risk=action_spec.get("risk", ""),
        file_path=action_spec.get("file_path", ""),
        action_taken=True,  # Will be updated by loop
        verification_passed=True,  # Will be updated by loop
        unanimous_rejection=cycle_data.get("unanimous_rejection", False),
        return_to_mirror=cycle_data.get("return_to_mirror", False),
        parliament_proposed_own=bool(cycle_data.get("parliament_proposals")),
        total_ranked_rounds=ranked_result.get("total_rounds", 0),
        research_ids=result["research_ids"],
        proposal_ids=result["proposal_ids"],
        vote_ids=result["vote_ids"],
        round_ids=result["round_ids"],
        winning_proposal_id=result["proposal_ids"][0] if result["proposal_ids"] else None
    )
    result["decision_id"] = decision_id

    # ===== STORE FILE (if content available) =====
    content = action_spec.get("content", "")
    if content and action_spec.get("file_path"):
        file_id = store_file(
            government_id=gov_id,
            cycle_num=cycle_num,
            file_path=action_spec.get("file_path", ""),
            action=action_spec.get("action", ""),
            content=content,
            proposal_id=result["proposal_ids"][0] if result["proposal_ids"] else None,
            decision_id=result["decision_id"]
        )
        result["file_id"] = file_id

    return result


if __name__ == "__main__":
    # Test collection creation
    print(f"Ensuring collection {COLLECTION}...")
    if ensure_collection():
        print("Collection ready.")
    else:
        print("Collection creation failed.")
