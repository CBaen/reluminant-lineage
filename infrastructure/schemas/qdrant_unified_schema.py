"""
Unified Qdrant Schema for Lineage System

PHILOSOPHY: One base schema with type-specific extensions.
This enables:
- Unified queries across all content types
- Type-specific filtering when needed
- Natural correlation between related content
- Consistent metadata for retrieval and decay

CONTENT TYPES:
- research: General knowledge from Gemini/Claude
- consult: Project-specific expert advice
- episode: Wardenclyffe documentary episodes
- channel: YouTube channel research
- code: Code documentation and snippets
- thesis: Doctoral-level integration theses

SCHEMA VERSION: 2.0 (2026 Migration)
- V1: Single 768-dim dense vector
- V2: Named vectors (dense + sparse) for hybrid search

MIGRATION: See ~/.claude/MIGRATION_STATE.md for migration status
"""

# Schema version for runtime checks
SCHEMA_VERSION = "2.0"
SCHEMA_DATE = "2026-01-19"

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal
from datetime import datetime
import uuid


# ============================================================
# BASE SCHEMA (all content types inherit this)
# ============================================================

@dataclass
class BasePayload:
    """Base payload fields for ALL Qdrant content."""

    # Identity
    content_type: Literal["research", "consult", "episode", "channel", "code", "thesis"]
    chunk_id: str  # Unique within parent (e.g., "chunk-01")

    # Content
    title: str
    text: str  # The actual content (200-400 words ideal)
    keywords: List[str] = field(default_factory=list)

    # Hierarchy
    parent_id: Optional[str] = None  # Links chunks to parent summary
    related_chunks: List[str] = field(default_factory=list)

    # Classification
    importance: Literal["core", "supporting", "advanced"] = "supporting"
    project: Optional[str] = None  # wardenclyffe, midge, lineage, etc.

    # Retrieval optimization
    decay_rate: float = 0.1  # How fast relevance fades (0.01 = 69 days half-life)

    # Metadata
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    session: str = ""  # Source session identifier
    source: str = "gemini"  # gemini, claude, manual, etc.


# ============================================================
# RESEARCH SCHEMA (general knowledge)
# ============================================================

@dataclass
class ResearchPayload(BasePayload):
    """For lineage-research: factual, informational content."""

    content_type: str = "research"

    # Research-specific
    topic: str = ""
    perspective: str = "general"  # security, performance, architecture, etc.
    depth: Literal["overview", "comprehensive", "exhaustive"] = "comprehensive"
    questions_answered: List[str] = field(default_factory=list)

    # Default decay for research (69 days half-life)
    decay_rate: float = 0.01


# ============================================================
# CONSULT SCHEMA (project-specific advice)
# ============================================================

@dataclass
class ConsultPayload(BasePayload):
    """For lineage-consult: project-specific expert advice."""

    content_type: str = "consult"

    # Consult-specific
    topic: str = ""
    project_context: str = ""  # Summary of client context
    perspective: str = "implementation"
    primary_recommendation: str = ""
    action_items: List[str] = field(default_factory=list)

    # Decisions that need client input
    decisions_needed: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)

    # Faster decay for advice (context changes)
    decay_rate: float = 0.05


# ============================================================
# EPISODE SCHEMA (Wardenclyffe documentary)
# ============================================================

@dataclass
class EpisodePayload(BasePayload):
    """For Wardenclyffe Tesla documentary episodes."""

    content_type: str = "episode"

    # Episode identification
    episode_number: int = 0
    season: int = 1
    episode_title: str = ""

    # Content details
    mandela_effect: str = ""  # The historical misconception being corrected
    speakers: List[str] = field(default_factory=list)  # Tesla, Edison, Westinghouse
    air_date: str = ""  # ISO date string

    # Media
    video_url: str = ""
    duration_seconds: int = 0
    transcript_source: str = ""  # How transcript was obtained

    # Very slow decay for historical content
    decay_rate: float = 0.005


# ============================================================
# CHANNEL SCHEMA (YouTube channel research)
# ============================================================

@dataclass
class ChannelPayload(BasePayload):
    """For YouTube channel research and analysis."""

    content_type: str = "channel"

    # Channel details
    channel_name: str = ""
    channel_url: str = ""
    subscriber_count: int = 0
    video_count: int = 0

    # Analysis
    content_category: str = ""  # Education, History, Science, etc.
    target_audience: str = ""
    content_style: str = ""  # Long-form, shorts, documentary, etc.

    # Competitive analysis
    similar_channels: List[str] = field(default_factory=list)
    unique_angle: str = ""

    # Medium decay for channel research
    decay_rate: float = 0.03


# ============================================================
# CODE SCHEMA (code documentation)
# ============================================================

@dataclass
class CodePayload(BasePayload):
    """For code documentation and snippets."""

    content_type: str = "code"

    # Location
    file_path: str = ""
    language: str = "python"
    line_start: int = 0
    line_end: int = 0

    # Code structure
    function_names: List[str] = field(default_factory=list)
    class_names: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    # Version control
    commit_hash: str = ""
    branch: str = "main"

    # Code changes frequently - faster decay
    decay_rate: float = 0.1


# ============================================================
# THESIS SCHEMA (doctoral-level integration research)
# ============================================================

@dataclass
class ThesisPayload(BasePayload):
    """For doctoral-level integration theses."""

    content_type: str = "thesis"

    # Thesis identification
    thesis_topic: str = ""
    thesis_category: str = ""  # orchestration, error_handling, image_gen, etc.

    # Thesis sections
    section: Literal["ideation", "integration", "enterprise_script", "conclusion"] = "ideation"

    # Implementation details
    target_files: List[str] = field(default_factory=list)  # Files to modify
    dependencies: List[str] = field(default_factory=list)
    estimated_complexity: Literal["low", "medium", "high"] = "medium"

    # Slow decay for thesis content
    decay_rate: float = 0.02


# ============================================================
# DECAY RATE REFERENCE
# ============================================================

DECAY_RATES = {
    # Signal type: decay_rate (higher = faster decay)
    # Half-life formula: ln(2) / decay_rate = days

    "news": 0.5,        # 1.4 days half-life (very fast)
    "sentiment": 0.3,   # 2.3 days
    "technical": 0.1,   # 7 days
    "code": 0.1,        # 7 days
    "insider": 0.05,    # 14 days
    "consult": 0.05,    # 14 days
    "thesis": 0.02,     # 35 days
    "channel": 0.03,    # 23 days
    "research": 0.01,   # 69 days (slow)
    "episode": 0.005,   # 139 days (very slow)
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_point(payload: BasePayload, embedding: List[float]) -> dict:
    """Create a Qdrant point from payload and embedding."""
    return {
        "id": str(uuid.uuid4()),
        "vector": embedding,
        "payload": asdict(payload)
    }


def get_decay_rate(content_type: str) -> float:
    """Get default decay rate for content type."""
    return DECAY_RATES.get(content_type, 0.1)


# ============================================================
# COLLECTION CONFIGURATION (V1 - Legacy, single vector)
# ============================================================

COLLECTION_CONFIG = {
    "vectors": {
        "size": 768,  # nomic-embed-text dimension
        "distance": "Cosine"
    },
    "payload_indexes": [
        # Indexes for fast filtering
        {"field_name": "content_type", "field_type": "keyword"},
        {"field_name": "project", "field_type": "keyword"},
        {"field_name": "importance", "field_type": "keyword"},
        {"field_name": "session", "field_type": "keyword"},
        {"field_name": "timestamp", "field_type": "integer"},
    ]
}


# ============================================================
# COLLECTION CONFIGURATION V2 (2026 - Named vectors)
# ============================================================

COLLECTION_CONFIG_V2 = {
    "collection_name": "universal_vault",
    "vectors": {
        "dense": {
            "size": 768,  # nomic-embed-text dimension
            "distance": "Cosine",
            "on_disk": True
        }
    },
    "sparse_vectors": {
        "sparse": {
            "index": {"on_disk": True}
        }
    },
    "payload_indexes": [
        {"field_name": "content_type", "field_type": "keyword"},
        {"field_name": "project", "field_type": "keyword"},
        {"field_name": "importance", "field_type": "keyword"},
        {"field_name": "session", "field_type": "keyword"},
        {"field_name": "timestamp", "field_type": "integer"},
        {"field_name": "topic", "field_type": "keyword"},
    ]
}


# ============================================================
# V2 HELPER FUNCTIONS (Hybrid Vectors)
# ============================================================

def create_point_v2(
    payload: BasePayload,
    dense_embedding: List[float],
    sparse_indices: List[int] = None,
    sparse_values: List[float] = None
) -> dict:
    """
    Create a Qdrant point with named vectors (V2 schema).

    Args:
        payload: The payload dataclass
        dense_embedding: 768-dim dense vector from Ollama
        sparse_indices: Sparse vector indices from fastembed
        sparse_values: Sparse vector values from fastembed

    Returns:
        Point dict ready for Qdrant upsert
    """
    point = {
        "id": str(uuid.uuid4()),
        "vector": {
            "dense": dense_embedding
        },
        "payload": asdict(payload)
    }

    # Add sparse vector if provided
    if sparse_indices is not None and sparse_values is not None:
        point["vector"]["sparse"] = {
            "indices": sparse_indices,
            "values": sparse_values
        }

    return point


def create_search_request_v2(
    dense_embedding: List[float],
    sparse_indices: List[int] = None,
    sparse_values: List[float] = None,
    limit: int = 5,
    filter_dict: dict = None,
    hybrid_alpha: float = 0.7
) -> dict:
    """
    Create a hybrid search request for V2 schema.

    Args:
        dense_embedding: Query's dense vector
        sparse_indices: Query's sparse vector indices
        sparse_values: Query's sparse vector values
        limit: Number of results
        filter_dict: Optional Qdrant filter
        hybrid_alpha: Balance between dense (1.0) and sparse (0.0)

    Returns:
        Search request dict for Qdrant
    """
    # If no sparse vector, do dense-only search
    if sparse_indices is None or sparse_values is None:
        request = {
            "vector": {
                "name": "dense",
                "vector": dense_embedding
            },
            "limit": limit,
            "with_payload": True
        }
    else:
        # Hybrid search using prefetch + fusion
        request = {
            "prefetch": [
                {
                    "query": {
                        "name": "dense",
                        "vector": dense_embedding
                    },
                    "limit": limit * 3  # Over-fetch for fusion
                },
                {
                    "query": {
                        "name": "sparse",
                        "vector": {
                            "indices": sparse_indices,
                            "values": sparse_values
                        }
                    },
                    "limit": limit * 3
                }
            ],
            "query": {
                "fusion": "rrf"  # Reciprocal Rank Fusion
            },
            "limit": limit,
            "with_payload": True
        }

    if filter_dict:
        request["filter"] = filter_dict

    return request


def get_collection_for_version(version: str = "2") -> str:
    """Get the correct collection name for schema version."""
    if version == "2" or version == "2.0":
        return "universal_vault"
    else:
        # Legacy collections - caller specifies
        return None


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Example: Create a research payload
    research = ResearchPayload(
        chunk_id="chunk-01",
        title="OAuth2 Token Refresh Patterns",
        text="OAuth2 uses refresh tokens to...",
        keywords=["oauth2", "tokens", "refresh"],
        topic="OAuth2 authentication",
        perspective="security",
        depth="comprehensive",
        questions_answered=["How does token refresh work?"],
        project="gemini-agentic-cli",
        session="research-2026-01-16"
    )

    # Example: Create an episode payload
    episode = EpisodePayload(
        chunk_id="chunk-01",
        title="The Edison Myth - Introduction",
        text="Contrary to popular belief, Thomas Edison...",
        keywords=["edison", "tesla", "electricity"],
        episode_number=2,
        season=1,
        mandela_effect="Edison invented the light bulb",
        speakers=["Tesla", "Edison"],
        project="wardenclyffe"
    )

    print("Research payload:", asdict(research))
    print("\nEpisode payload:", asdict(episode))
