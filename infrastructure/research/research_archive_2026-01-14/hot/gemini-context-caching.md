---
topic: "gemini-context-caching"
category: "gemini"
tier: "hot"
tags:
  - "gemini"
  - "caching"
  - "api"
  - "pricing"
  - "implementation"
  - "comparison"
  - "claude"
created: "2026-01-11 06:15 PM"
---

## 1. OVERVIEW

Gemini's context caching reduces costs and latency by storing frequently reused prompt parts.

### Two Types of Caching

**Implicit Caching**: Automatic, ~5-6 min TTL, no guarantee
**Explicit Caching**: User-controlled, customizable TTL, guaranteed savings

## 2. API MECHANISM

### Cache Creation Process
- API call to `v1beta/cachedContents` endpoint
- Submit large static content (system instructions, examples, documents)
- Google processes and stores KV cache with TTL
- Returns unique identifier: `cachedContents/xxxxxxxx`

### TTL Management
- Default: 1 hour
- Customizable via `ttl` parameter
- Can update existing cache expire_time
- Automatic deletion after expiration

### Using Cached Content
- Reference cache by name in `generateContent` calls
- Include new user input alongside cache reference
- Model loads cached state, processes new info
- Reusable across conversations/users

## 3. COST SAVINGS

### Billing Structure
- **Creation**: Standard input token rate (one-time)
- **Reuse**: Cached tokens FREE, pay only new inputs + outputs
- **Discount**: Up to 90% cost reduction possible

### Example (50k token document, 100 reuses):
- Without caching: $375
- With caching: $3.75 + $0.50 = $4.25
- **Savings: 98.9%**

## 4. GEMINI vs CLAUDE CACHING

### Architecture
| Aspect | Gemini | Claude |
|--------|--------|--------|
| Model | Explicit, stateful server objects | Implicit, in-band XML tags |
| API | Create `CachedContent` object | Use `<cache>` tags in prompt |
| Lifecycle | User-managed | Automatic |
| Scope | Cross-session/user | Single conversation |
| Cost | Free to reuse | 5-10x discount rate |

### Pricing Comparison
**Gemini** (100k tokens):
- Create: $2 (standard rate)
- Reuse: $0 (free)
- Total: ~$2 after many uses

**Claude** (100k tokens):
- First: $10 (standard rate)
- Reuse: ~$1 each (discounted)
- Total: Escalating with use count

### Performance
Both provide dramatic TTFT improvements:
- Gemini: Pre-computed state loads instantly
- Claude: Bypasses prefix re-processing
- Latency: Seconds → sub-seconds for first token
- Impact: Interactive large-document apps become responsive

## 5. IMPLEMENTATION

### Python SDK: Create Cache
```python
import google.generativeai as genai

client = genai.Client()
cache = client.caches.create(
    model="models/gemini-2.0-flash",
    system_instruction="You are an expert reviewer.",
    cached_content={"text": "Review examples..."},
    ttl=3600  # 1 hour
)
cache_name = cache.name
```

### Python SDK: Use Cache
```python
response = client.models.generate_content(
    model="models/gemini-2.0-flash",
    contents=[{
        "role": "user",
        "parts": [{"text": "Review this code..."}]
    }],
    cached_content=cache_name
)
```

### Python SDK: Manage TTL
```python
# Update TTL
client.caches.update(name=cache_name, expire_time={"seconds": 172800})

# Delete
client.caches.delete(name=cache_name)

# List all
all_caches = client.caches.list()
```

### REST API: Create
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/cachedContents?key=KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models/gemini-2.0-flash",
    "display_name": "examples",
    "cached_content": [{"parts": [{"text": "..."}]}],
    "ttl": "3600s"
  }'
```

Response:
```json
{
  "name": "cachedContents/abc123",
  "model": "models/gemini-2.0-flash",
  "usageMetadata": {"cachedInputTokens": 5000},
  "expireTime": "2026-01-11T19:15:00Z"
}
```

### REST API: Use Cache
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "cachedContent": "cachedContents/abc123",
    "contents": [{
      "role": "user",
      "parts": [{"text": "Review this..."}]
    }]
  }'
```

## 6. BEST PRACTICES

### When to Use
- Repetitive prompt prefixes
- Few-shot examples (unchanging)
- Chat with long system instructions
- Batch processing same context
- Document analysis (multiple queries)

### Cache Sizing
- Match model context window (100k-2M tokens)
- Start small, grow as needed
- Balance creation cost vs. reuse benefit

### Cost Optimization
- Cache expensive parts: long instructions, examples, documents
- Use cheaper model for cache creation if possible
- Monitor usage via billing dashboard
- Tune TTL: balance storage vs. recreation cost

### Batch Processing
- **Homogeneous**: Group prompts with same cache (most efficient)
- **Asynchronous**: Pool of caches for different task types

### TTL Strategies
- Session-based: Duration of user session
- Activity-based: Auto-discard if unused
- Content-based: Invalidate on data changes
- LRU: Keep most-used contexts, discard least-used

## 7. KEY TAKEAWAYS

1. Explicit caching: Object-based, cross-session reusable
2. Cost savings: 90% reduction, especially large repetitive contexts
3. Latency: Sub-second first token with cached content
4. vs Claude: Different models (stateful objects vs. inline tags)
5. Best for: Batch processing, high-reuse scenarios
6. Simple SDK: Straightforward Python/REST integration
7. TTL critical: Balance storage and recreation overhead
