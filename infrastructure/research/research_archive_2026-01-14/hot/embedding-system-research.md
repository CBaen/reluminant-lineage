# Embedding System Research for Local Qdrant Vector Search

## 2026-01-13 | Session: EmbeddingResearch

---

## Executive Summary

For a solo operator with local Qdrant (localhost:6333), i7-11850H, 48GB RAM, and 4GB GPU, the recommended path is:

**Primary Recommendation: Hybrid Approach**
1. **Local embeddings with nomic-embed-text-v1.5** via Ollama (runs easily on 4GB GPU)
2. **Optional Gemini API fallback** for high-quality embeddings when batch processing
3. **Qdrant hybrid search** combining dense + sparse (BM25) vectors

---

## 1. GEMINI EMBEDDINGS

### Does Gemini CLI Support Embeddings?

**No, not directly.** The Gemini CLI does not have a native embedding command. There is an open GitHub issue (#5150) requesting this feature. Embeddings require the Python SDK or REST API.

### Available Models

| Model | Dimensions | Status | Notes |
|-------|-----------|--------|-------|
| `gemini-embedding-001` | 3072 (default), 128-3072 flexible | **Current** | Uses Matryoshka learning |
| `text-embedding-004` | 768 | Deprecating Jan 14, 2026 | Legacy |
| `embedding-001` | 768 | Deprecated Oct 2025 | Obsolete |

### API Usage

```python
from google import genai

client = genai.Client(api_key='YOUR_API_KEY')

# Single embedding
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents="Your text here",
    config={
        "task_type": "RETRIEVAL_DOCUMENT",  # or RETRIEVAL_QUERY, SEMANTIC_SIMILARITY, etc.
        "output_dimensionality": 768  # Optional: reduce from 3072 default
    }
)
embedding = result.embeddings[0].values

# Batch embedding
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=["Text 1", "Text 2", "Text 3"]
)
```

### Task Types (Optimize for Use Case)

| Task Type | Use For |
|-----------|---------|
| `RETRIEVAL_DOCUMENT` | Indexing documents for search |
| `RETRIEVAL_QUERY` | Search queries |
| `SEMANTIC_SIMILARITY` | Comparing text similarity |
| `CLASSIFICATION` | Categorizing texts |
| `CLUSTERING` | Grouping similar texts |
| `CODE_RETRIEVAL_QUERY` | Code search |

### Pricing & Limits

**Free Tier:**
- gemini-embedding-001: Free
- Rate limits: ~100 RPM, 1,000 RPD for embeddings

**Paid Tier:**
- Standard: $0.15 per 1M tokens
- Batch: $0.075 per 1M tokens (50% discount)

**Note:** December 2025 saw 50-80% rate limit reductions. Use batch API for bulk processing.

### Sources
- [Gemini Embeddings Documentation](https://ai.google.dev/gemini-api/docs/embeddings)
- [Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Qdrant + Gemini Integration](https://qdrant.tech/documentation/embeddings/gemini/)

---

## 2. LOCAL EMBEDDING MODELS

### What Runs on 4GB GPU + 48GB RAM?

**All of these run comfortably:**

| Model | Size | Dimensions | VRAM | Quality (MTEB) | Speed |
|-------|------|------------|------|----------------|-------|
| `all-MiniLM-L6-v2` | 33M | 384 | <500MB | 56% | Fastest (14.7ms/1K) |
| `all-mpnet-base-v2` | 110M | 768 | <1GB | Higher | Fast (<30ms) |
| `nomic-embed-text-v1.5` | 137M | 768 (64-768 flexible) | <500MB | Top tier | Fast |
| `bge-m3` | ~560M | 1024 | ~1-2GB | State-of-art | Moderate |
| `bge-large-en-v1.5` | 335M | 1024 | ~1GB | High | Moderate |

### Recommended: nomic-embed-text-v1.5

**Why nomic-embed-text:**
- Open source, Apache 2.0 license
- Matryoshka learning (variable dimensions 64-768)
- Long context (2048 tokens vs 512 for MiniLM)
- Outperforms OpenAI ada-002 and text-embedding-3-small
- Only ~275MB download, ~500MB VRAM
- Available via Ollama for easy local deployment

```bash
# Install via Ollama
ollama pull nomic-embed-text

# Generate embeddings
ollama embeddings --model nomic-embed-text "Your text here"
```

### Alternative: BGE-M3 (Hybrid King)

**Why BGE-M3 is special:**
- Generates BOTH dense AND sparse embeddings in one pass
- 1024-dimensional dense vectors
- Lexical weights (BM25-like) for sparse retrieval
- Multi-vector (ColBERT) for re-ranking
- 8192 token context
- 100+ languages

```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

output = model.encode(
    ["Your text here"],
    return_dense=True,
    return_sparse=True,
    return_colbert_vecs=False
)

dense_embedding = output['dense_vecs'][0]  # 1024-dim
sparse_weights = output['lexical_weights'][0]  # {token: weight, ...}
```

### sentence-transformers Usage

```python
from sentence_transformers import SentenceTransformer

# Load model (auto-detects GPU)
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5",
                            model_kwargs={"torch_dtype": "float16"})

# Batch embedding
sentences = ["Text 1", "Text 2", "Text 3"]
embeddings = model.encode(sentences,
                          batch_size=32,
                          show_progress_bar=True)
```

### Performance Tips

1. **Use fp16**: Half-precision saves VRAM with minimal quality loss
2. **Batch processing**: Encode multiple texts at once (batch_size=32-64)
3. **ONNX backend**: For short texts, ONNX with GPU gives 1.46x speedup

### Sources
- [Sentence Transformers Efficiency](https://sbert.net/docs/sentence_transformer/usage/efficiency.html)
- [nomic-embed-text on Ollama](https://ollama.com/library/nomic-embed-text)
- [BGE-M3 on HuggingFace](https://huggingface.co/BAAI/bge-m3)
- [Open Source Embedding Benchmarks](https://research.aimultiple.com/open-source-embedding-models/)

---

## 3. HYBRID APPROACH

### Using Gemini for Embedding + Qdrant Storage

```python
from google import genai
import requests

QDRANT_URL = "http://localhost:6333"

def get_gemini_embedding(text, task_type="RETRIEVAL_DOCUMENT"):
    client = genai.Client(api_key='YOUR_API_KEY')
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config={
            "task_type": task_type,
            "output_dimensionality": 768  # Match your collection
        }
    )
    return result.embeddings[0].values

def store_in_qdrant(collection, point_id, vector, payload):
    url = f"{QDRANT_URL}/collections/{collection}/points"
    data = {
        "points": [{
            "id": point_id,
            "vector": vector,
            "payload": payload
        }]
    }
    return requests.put(url, json=data).json()
```

### Batch Embedding Strategy

```python
import time

def batch_embed_with_rate_limiting(texts, batch_size=10, delay=1.0):
    """Embed texts in batches with rate limiting for free tier."""
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=batch,
            config={"task_type": "RETRIEVAL_DOCUMENT"}
        )
        all_embeddings.extend([e.values for e in result.embeddings])

        if i + batch_size < len(texts):
            time.sleep(delay)  # Respect rate limits

    return all_embeddings
```

### Incremental Embedding (Only New Documents)

```python
import hashlib

def get_content_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def needs_embedding(collection, content_hash):
    """Check if document already exists in Qdrant."""
    url = f"{QDRANT_URL}/collections/{collection}/points/scroll"
    response = requests.post(url, json={
        "filter": {
            "must": [{"key": "content_hash", "match": {"value": content_hash}}]
        },
        "limit": 1
    })
    result = response.json()
    return len(result.get("result", {}).get("points", [])) == 0

def embed_if_new(collection, text, metadata):
    content_hash = get_content_hash(text)
    if needs_embedding(collection, content_hash):
        embedding = get_gemini_embedding(text)
        metadata["content_hash"] = content_hash
        store_in_qdrant(collection, str(uuid.uuid4()), embedding, metadata)
        return True
    return False
```

---

## 4. QDRANT-SPECIFIC CONSIDERATIONS

### Named Vectors (Multiple Embedding Types)

Configure collection with multiple vector types:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, SparseVectorParams

client = QdrantClient(url="http://localhost:6333")

# Create collection with named vectors
client.recreate_collection(
    collection_name="research",
    vectors_config={
        "dense": VectorParams(size=768, distance=Distance.COSINE),
        "semantic": VectorParams(size=1024, distance=Distance.COSINE),  # For BGE-M3
    },
    sparse_vectors_config={
        "sparse": SparseVectorParams()
    }
)
```

### Storing Points with Multiple Vectors

```python
client.upsert(
    collection_name="research",
    points=[{
        "id": "doc-123",
        "vector": {
            "dense": [0.1, 0.2, ...],  # 768-dim nomic embedding
            "semantic": [0.3, 0.4, ...],  # 1024-dim BGE-M3 embedding
        },
        "payload": {"content": "...", "topic": "..."}
    }]
)
```

### Hybrid Search: Dense + Sparse (BM25)

```python
from qdrant_client.models import SparseVector, Prefetch, FusionQuery, Fusion

# Hybrid search with RRF fusion
results = client.query_points(
    collection_name="research",
    prefetch=[
        # Sparse (BM25-like) search
        Prefetch(
            query=SparseVector(
                indices=[1, 42, 100],  # Token indices
                values=[0.5, 0.8, 0.3]  # TF-IDF weights
            ),
            using="sparse",
            limit=20
        ),
        # Dense semantic search
        Prefetch(
            query=[0.1, 0.2, ...],  # Your query embedding
            using="dense",
            limit=20
        )
    ],
    query=FusionQuery(fusion=Fusion.RRF),  # Reciprocal Rank Fusion
    limit=10
)
```

### Fusion Methods

| Method | Description | Use When |
|--------|-------------|----------|
| **RRF** | Reciprocal Rank Fusion - combines by rank position | Default, works well generally |
| **DBSF** | Distribution-Based Score Fusion - normalizes scores | When score magnitudes vary |

### BM25 Configuration in Qdrant

```python
# Qdrant can compute IDF automatically
client.recreate_collection(
    collection_name="research",
    sparse_vectors_config={
        "bm25_sparse_vector": SparseVectorParams(
            modifier="idf"  # Qdrant handles IDF calculation
        )
    }
)
```

### Sources
- [Qdrant Hybrid Queries](https://qdrant.tech/documentation/concepts/hybrid-queries/)
- [Qdrant Sparse Vectors](https://qdrant.tech/articles/sparse-vectors/)
- [BGE-M3 with Qdrant](https://yuniko.software/bge-m3-qdrant/)

---

## 5. IMPLEMENTATION PATH

### Recommended Changes to qdrant-store.py

```python
#!/usr/bin/env python3
"""
qdrant-store.py - Store research in Qdrant with real semantic embeddings

Supports:
- Local embeddings via Ollama (nomic-embed-text)
- Gemini API embeddings (fallback)
- Incremental embedding (skip already-embedded documents)
"""

import subprocess
import json
import os

# Embedding provider priority
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama")  # ollama, gemini, hash

def get_ollama_embedding(text):
    """Generate embedding using local Ollama model."""
    try:
        result = subprocess.run(
            ["ollama", "embeddings", "--model", "nomic-embed-text", text],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("embedding", [])
    except Exception as e:
        print(f"Ollama embedding failed: {e}", file=sys.stderr)
    return None

def get_gemini_embedding(text):
    """Generate embedding using Gemini API."""
    try:
        from google import genai
        client = genai.Client()  # Uses GOOGLE_API_KEY env var
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config={"task_type": "RETRIEVAL_DOCUMENT", "output_dimensionality": 768}
        )
        return list(result.embeddings[0].values)
    except Exception as e:
        print(f"Gemini embedding failed: {e}", file=sys.stderr)
    return None

def get_embedding(text):
    """Get embedding with fallback chain."""
    if EMBEDDING_PROVIDER == "ollama":
        embedding = get_ollama_embedding(text)
        if embedding:
            return embedding

    if EMBEDDING_PROVIDER in ["gemini", "ollama"]:  # fallback from ollama
        embedding = get_gemini_embedding(text)
        if embedding:
            return embedding

    # Final fallback: hash-based pseudo-embedding
    return get_hash_embedding(text)
```

### Embedding at Ingestion Time vs Batch Post-Processing

**Ingestion Time (Recommended for Research):**
- Embed immediately when storing
- Ensures all documents are searchable
- Simpler implementation

**Batch Post-Processing:**
- Queue documents without embeddings
- Process in batches during idle time
- Better for high-volume ingestion with rate limits

```python
# Batch post-processing script
def batch_embed_unembedded():
    """Find and embed documents that only have hash embeddings."""
    url = f"{QDRANT_URL}/collections/research/points/scroll"
    response = requests.post(url, json={
        "filter": {
            "must": [{"key": "embedding_type", "match": {"value": "hash"}}]
        },
        "limit": 100,
        "with_vectors": False
    })

    for point in response.json()["result"]["points"]:
        text = point["payload"]["content"]
        new_embedding = get_ollama_embedding(text)
        if new_embedding:
            update_point_vector(point["id"], new_embedding)
            update_point_payload(point["id"], {"embedding_type": "semantic"})
```

### Caching Embeddings

```python
import hashlib
from pathlib import Path
import json

CACHE_DIR = Path.home() / ".claude" / "embedding_cache"
CACHE_DIR.mkdir(exist_ok=True)

def get_cached_embedding(text, model="nomic"):
    """Check cache before computing embedding."""
    cache_key = hashlib.sha256(f"{model}:{text}".encode()).hexdigest()
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if cache_file.exists():
        return json.loads(cache_file.read_text())

    return None

def cache_embedding(text, embedding, model="nomic"):
    """Store embedding in cache."""
    cache_key = hashlib.sha256(f"{model}:{text}".encode()).hexdigest()
    cache_file = CACHE_DIR / f"{cache_key}.json"
    cache_file.write_text(json.dumps(embedding))
```

---

## 6. RECOMMENDED IMPLEMENTATION ORDER

### Phase 1: Local Semantic Search (Immediate)

1. Install Ollama: `winget install ollama`
2. Pull model: `ollama pull nomic-embed-text`
3. Update qdrant-store.py to use Ollama embeddings
4. Test with existing research collection

### Phase 2: Hybrid Search (Next)

1. Create new collection with named vectors
2. Add sparse vector support for BM25
3. Implement hybrid query function
4. Migrate existing data with new embeddings

### Phase 3: Advanced Features (Later)

1. Add BGE-M3 for multi-vector retrieval
2. Implement re-ranking with cross-encoders
3. Add embedding caching layer
4. Create batch re-embedding job

---

## 7. MODEL COMPARISON SUMMARY

| Model | Dims | Quality | Speed | Cost | Hybrid |
|-------|------|---------|-------|------|--------|
| **nomic-embed-text-v1.5** | 768 | High | Fast | Free (local) | No |
| **BGE-M3** | 1024 | Highest | Moderate | Free (local) | Yes (built-in) |
| **gemini-embedding-001** | 768-3072 | Very High | API latency | Free tier / $0.15/1M | No |
| **all-MiniLM-L6-v2** | 384 | Moderate | Fastest | Free (local) | No |

**Winner for Your Setup: nomic-embed-text-v1.5**
- Best balance of quality, speed, and simplicity
- Runs perfectly on 4GB GPU
- Easy Ollama integration
- Upgrade to BGE-M3 when you need hybrid search

---

## Sources

- [Gemini Embeddings Documentation](https://ai.google.dev/gemini-api/docs/embeddings)
- [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Qdrant + Gemini Integration](https://qdrant.tech/documentation/embeddings/gemini/)
- [Qdrant Hybrid Queries](https://qdrant.tech/documentation/concepts/hybrid-queries/)
- [Qdrant Sparse Vectors](https://qdrant.tech/articles/sparse-vectors/)
- [nomic-embed-text on Ollama](https://ollama.com/library/nomic-embed-text)
- [BGE-M3 on HuggingFace](https://huggingface.co/BAAI/bge-m3)
- [Sentence Transformers Efficiency](https://sbert.net/docs/sentence_transformer/usage/efficiency.html)
- [Open Source Embedding Benchmarks](https://research.aimultiple.com/open-source-embedding-models/)
- [Best Open Source Embedding Models](https://supermemory.ai/blog/best-open-source-embedding-models-benchmarked-and-ranked/)
