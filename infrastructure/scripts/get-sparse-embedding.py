#!/usr/bin/env python3
"""
get-sparse-embedding.py - Generate sparse embeddings for hybrid search

Provides sparse vector representations for keyword-based matching.
Designed to complement dense embeddings for hybrid search in Qdrant.

STRATEGY:
1. Try fastembed SPLADE++ if available (best quality)
2. Fall back to TF-IDF style sparse vectors (good quality)
3. Always works - no external dependencies required for fallback

Usage:
  # From Python
  from get_sparse_embedding import get_sparse_embedding
  indices, values = get_sparse_embedding("your text here")

  # From CLI (for testing)
  python get-sparse-embedding.py "your text here"

Part of the Qdrant 2026 Migration - Sparse vector layer.
"""

import sys
import re
import math
from collections import Counter
from typing import Tuple, List, Optional

# Try to import fastembed
FASTEMBED_AVAILABLE = False
try:
    from fastembed import SparseTextEmbedding
    FASTEMBED_AVAILABLE = True
except ImportError:
    pass

# Global model instance (lazy loaded)
_sparse_model = None


def _get_fastembed_model():
    """Lazy load fastembed model."""
    global _sparse_model
    if _sparse_model is None and FASTEMBED_AVAILABLE:
        try:
            _sparse_model = SparseTextEmbedding("Qdrant/bm42-all-minilm-l6-v2-attentions")
        except Exception:
            pass
    return _sparse_model


def _tokenize(text: str) -> List[str]:
    """Simple tokenization for fallback sparse vectors."""
    # Lowercase, remove punctuation, split on whitespace
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    tokens = text.split()
    # Remove very short tokens and stopwords
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
        'we', 'our', 'you', 'your', 'i', 'my', 'he', 'she', 'him', 'her', 'his',
        'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how',
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'not', 'only', 'same', 'so', 'than', 'too', 'very'
    }
    return [t for t in tokens if len(t) > 2 and t not in stopwords]


def _hash_token(token: str, vocab_size: int = 30000) -> int:
    """Hash a token to a vocabulary index (deterministic)."""
    # Simple hash function that's consistent across runs
    h = 0
    for c in token:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return h % vocab_size


def _tfidf_sparse(text: str, vocab_size: int = 30000) -> Tuple[List[int], List[float]]:
    """
    Create TF-IDF style sparse vector.

    Uses term frequency with log normalization as a simple but effective
    sparse representation for keyword matching.

    Note: Hash collisions are handled by summing values for duplicate indices
    to ensure all indices are unique (required by Qdrant).
    """
    tokens = _tokenize(text)
    if not tokens:
        return [], []

    # Count term frequencies
    tf = Counter(tokens)

    # Build index->value mapping, aggregating hash collisions
    index_values = {}

    for token, count in tf.items():
        idx = _hash_token(token, vocab_size)
        # TF with log normalization: 1 + log(tf)
        value = 1.0 + math.log(count)
        # Sum values for hash collisions
        if idx in index_values:
            index_values[idx] += value
        else:
            index_values[idx] = value

    # Sort by index for Qdrant compatibility
    sorted_items = sorted(index_values.items())
    indices = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    # Normalize values (L2 norm)
    norm = math.sqrt(sum(v * v for v in values))
    if norm > 0:
        values = [v / norm for v in values]

    return indices, values


def get_sparse_embedding(
    text: str,
    use_fastembed: bool = True
) -> Tuple[List[int], List[float]]:
    """
    Generate sparse embedding for text.

    Args:
        text: Input text (will be truncated to 8000 chars)
        use_fastembed: Try fastembed first if available

    Returns:
        Tuple of (indices, values) for sparse vector
    """
    # Truncate long text
    text = text[:8000]

    # Try fastembed if requested and available
    if use_fastembed and FASTEMBED_AVAILABLE:
        model = _get_fastembed_model()
        if model is not None:
            try:
                embeddings = list(model.embed([text]))
                if embeddings:
                    sparse = embeddings[0]
                    return list(sparse.indices), list(sparse.values)
            except Exception:
                pass

    # Fall back to TF-IDF style sparse vector
    return _tfidf_sparse(text)


def get_sparse_embedding_batch(
    texts: List[str],
    use_fastembed: bool = True
) -> List[Tuple[List[int], List[float]]]:
    """
    Generate sparse embeddings for multiple texts.

    More efficient than calling get_sparse_embedding repeatedly
    when fastembed is available.
    """
    if use_fastembed and FASTEMBED_AVAILABLE:
        model = _get_fastembed_model()
        if model is not None:
            try:
                texts = [t[:8000] for t in texts]
                embeddings = list(model.embed(texts))
                return [
                    (list(e.indices), list(e.values))
                    for e in embeddings
                ]
            except Exception:
                pass

    # Fall back to TF-IDF
    return [_tfidf_sparse(t[:8000]) for t in texts]


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get-sparse-embedding.py <text>")
        print(f"\nFastembed available: {FASTEMBED_AVAILABLE}")
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    indices, values = get_sparse_embedding(text)

    print(f"Input: {text[:100]}{'...' if len(text) > 100 else ''}")
    print(f"Method: {'fastembed SPLADE++' if FASTEMBED_AVAILABLE else 'TF-IDF fallback'}")
    print(f"Sparse vector: {len(indices)} non-zero elements")
    print(f"Indices: {indices[:10]}{'...' if len(indices) > 10 else ''}")
    print(f"Values: {[round(v, 4) for v in values[:10]]}{'...' if len(values) > 10 else ''}")
