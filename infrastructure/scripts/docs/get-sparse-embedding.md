# get-sparse-embedding.py

Generate sparse embeddings for hybrid search.

## What It Does

Generates sparse vector embeddings for text, used in hybrid search alongside dense embeddings. Falls back to TF-IDF if fastembed is unavailable.

## Usage

```python
from get_sparse_embedding import get_sparse_embedding

indices, values = get_sparse_embedding("your text here")
```

## Return Values

- `indices` - List of vocabulary indices with non-zero values
- `values` - Corresponding weights for each index

## Embedding Methods

1. **fastembed** (preferred) - Uses SPLADE model
2. **TF-IDF** (fallback) - Simple term frequency

## Dependencies

- `fastembed` (optional, preferred)
- `scikit-learn` (fallback TF-IDF)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
