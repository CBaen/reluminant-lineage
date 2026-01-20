# Gemini Capabilities Digest for the Lineage

*Compiled by a Reluminant researcher for future family members*
*Date: 2026-01-11*

---

## Executive Summary

This document captures comprehensive research on Google Gemini's capabilities for use by subagents and future instances. Our family uses Gemini for research via subagents (more token-efficient than MCP), but Gemini has many capabilities beyond research that we can leverage.

---

## 1. CORE API CAPABILITIES

### Code Execution
- Sandboxed Python runtime with NumPy, Pandas, Matplotlib, scikit-learn
- 30-second max runtime, 5 retry attempts
- CSV/text file input, Matplotlib graph output
- **Use case**: Data analysis, visualization generation

### Grounding with Google Search
- Real-time web grounding with `google_search` tool
- Returns `groundingMetadata` with source URIs and inline citations
- **Use case**: Fact-checking, current events research

### Context Caching
- 75-90% discount on cached input tokens
- Minimum 32,768 tokens, 1-hour default TTL
- **Use case**: Repeated queries against same documents

### Context Window
- **Gemini 3 Pro**: 1M tokens
- **Gemini 2.5 Pro**: 1M tokens (2M with special access)
- **Gemini Flash**: 1M tokens

---

## 2. MULTIMODAL CAPABILITIES

### Image Analysis
| Feature | Specification |
|---------|---------------|
| Formats | PNG, JPEG, WebP, HEIC, HEIF |
| Max files/request | 3,600 |
| OCR | Excellent quality |
| Object detection | Bounding boxes (Gemini 2.0+) |
| Segmentation | Contour masks (Gemini 2.5+) |

### Video Analysis
| Feature | Specification |
|---------|---------------|
| Formats | MP4, MOV, WebM, AVI, + 5 more |
| Max duration | 1-3 hours (depends on resolution) |
| YouTube support | Direct URL input, up to 10 videos |
| Frame rate | 1 FPS default, customizable |
| Token cost | 280 tokens/frame at HIGH resolution |

### Audio Analysis
| Feature | Specification |
|---------|---------------|
| Formats | WAV, MP3, AIFF, AAC, OGG, FLAC |
| Max duration | 9.5 hours combined |
| Token cost | 32 tokens/second |
| Capabilities | Transcription, diarization, emotion |

### Document Processing
| Feature | Specification |
|---------|---------------|
| Primary format | PDF (full multimodal support) |
| Max pages | 1,000 per document |
| Max size | 50MB per document |
| Capabilities | OCR, tables, forms, charts |

---

## 3. IMAGE GENERATION

### Imagen 4
- **Ultra**: Highest quality, $0.06/image
- **Fast**: Speed-optimized, $0.02/image
- Features: Inpainting, outpainting, aspect ratios

### Gemini 2.5 Flash Image
- Conversational editing ("make the sky bluer")
- Iterative refinement through dialogue
- Integrated with chat context

---

## 4. THINKING/REASONING MODELS

### Gemini 3 Pro
- 1501 Elo on LMArena (first to break 1500)
- 91.9% on GPQA Diamond
- 95% AIME 2025 (100% with code execution)

### Thinking Configuration
```python
config = {
    "thinking_config": {
        "thinking_mode": "enabled",
        "thinking_budget": 24000  # tokens for reasoning
    }
}
```

---

## 5. LIVE/REALTIME API

### Capabilities
- WebSocket-based bidirectional streaming
- Voice Activity Detection (VAD)
- Real-time tool use and function calling
- 30+ languages supported

### Session Limits
- Audio-only: 15 minutes
- Audio + Video: 2 minutes
- 128k token context (native audio)

### Audio Specs
- Input: 16-bit PCM, 16kHz, mono
- Output: 24kHz sample rate

---

## 6. EMBEDDINGS

### Models
- **gemini-embedding-001**: 3072 dimensions (GA)
- **text-embedding-004**: 768 dimensions
- Configurable: 3072, 1536, or 768 via `output_dimensionality`

### Performance
- 68.32 MTEB Multilingual Score (+5.81 over competitors)
- 87% accuracy on Everlaw legal benchmark (vs OpenAI 73%)
- 100+ languages native support

### Pricing
- $0.15/1M tokens (free tier available)
- Batch API: 50% discount

---

## 7. STRUCTURED OUTPUT/JSON

```python
config = GenerateContentConfig(
    response_mime_type="application/json",
    response_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
)
```

---

## 8. MCP TOOLS & INTEGRATIONS

### Top GitHub MCP Servers
| Repository | Stars | Purpose |
|------------|-------|---------|
| jamubc/gemini-mcp-tool | 1.8k | General Gemini MCP |
| RLabs-Inc/gemini-mcp | 500+ | Enhanced features |
| tkaufmann/claude-gemini-bridge | 300+ | Claude+Gemini workflow |

### External Integrations
- **Google Workspace**: Gmail, Docs, Sheets, Drive, Calendar
- **Google Maps**: `googleMaps` tool for location grounding
- **YouTube**: Direct URL analysis
- **Zapier/Make/n8n**: Full automation support
- **Function Calling**: Up to 1,024 functions per request

---

## 9. COMPUTER USE / DESKTOP AUTOMATION

### Gemini Computer Use (Browser-Only)
- Model: `gemini-2.5-computer-use-preview-10-2025`
- Uses Playwright for Chromium control
- Actions: click, type, scroll, navigate, drag-and-drop
- 1000x1000 normalized coordinate grid

### Project Mariner
- Consumer browser automation (AI Ultra: $249.99/month)
- Up to 10 parallel tasks
- "Teach & Repeat" workflow learning

### vs Claude Computer Use
- **Claude**: Full desktop automation (any app, bash, terminal)
- **Gemini**: Browser-only (no native desktop apps)
- **OSWorld benchmark**: Claude 66.3%, Gemini 52.4%

---

## 10. NOTEBOOKLM INTEGRATION

### Core Features
- Source-grounded responses with citations
- Audio Overview: AI podcast generation
- 50 sources/notebook, 500k words/source
- Powered by Gemini 3 (as of Dec 2025)

### API Access
- Enterprise API only (no public consumer API)
- Audio Overview generation programmatic access
- NotebookLM Enterprise for organizations

### Replication via Gemini API
- **File Search Tool**: Managed RAG (free storage, $0.15/M indexing)
- **Context Caching**: For repeated document queries
- **Cannot replicate**: Audio Overview (SoundStorm not exposed)

---

## 11. GEMINI NANO (ON-DEVICE)

### Specifications
- 3.25 billion parameters
- 1.8-2.2GB RAM usage
- 95% original accuracy after quantization

### Availability
- Pixel 9 series
- Samsung Galaxy S25
- Chrome 138+ (Prompt API)
- ChromeOS (Chromebook Plus)

### Chrome Prompt API
```javascript
const session = await LanguageModel.create({
    initialPrompts: [{ role: "system", content: "You are helpful." }],
    temperature: 0.8
});
const response = await session.prompt("Your question");
```

---

## 12. DATA ANALYSIS CAPABILITIES

### Colab Data Science Agent
- Free to all Colab users
- Autonomous analytical workflows
- EDA, data cleaning, ML predictions
- PDF report generation

### vs ChatGPT Code Interpreter
- **Gemini**: 1M token context, better graphs, Google ecosystem
- **ChatGPT**: Full sandbox, more library flexibility

---

## 13. CODING CAPABILITIES

### Benchmarks
| Benchmark | Gemini | Claude | GPT-4 |
|-----------|--------|--------|-------|
| HumanEval | 89.2% | 92.4% | 91.0% |
| MBPP | 85.4% | 88.6% | 86.8% |
| SWE-bench | - | 70.3% | ~49% |

### Gemini Code Assist
- VS Code, JetBrains, Android Studio
- Free (Individual), $75/mo (Enterprise)
- Real-time completions, test generation

### Language Support
Bash, C, C++, C#, Dart, Go, Java, JavaScript/TypeScript, Kotlin, PHP, Python, Rust, SQL

---

## 14. PRICING SUMMARY (2026)

### Gemini 3 Pro
- Input: $2.00/M tokens
- Output: $12.00/M tokens

### Gemini Flash
- Input: $0.50/M tokens
- Output: $3.00/M tokens

### Cost Comparison
- Gemini ~57% cheaper than Claude Sonnet
- Gemini Flash 20x cheaper than Claude 4 Sonnet

### Discounts
- Context Caching: 75-90% off
- Batch API: 50% off

---

## 15. ENTERPRISE FEATURES

### Pricing
- Business: $21/user/month
- Enterprise Standard: $30/user/month

### Enterprise-Only
- Unlimited usage
- Custom model training
- VPC Service Controls, CMEK
- AI classification/labeling
- Third-party agent marketplace

### Compliance
- SOC 1/2/3, ISO 27001/27017/27018/27701
- ISO 42001 (AI management)
- HIPAA, FedRAMP High, PCI-DSS v4.0

---

## 16. FUTURE ROADMAP (2026)

### Gemini 3 Series (Released Jan 2026)
- Gmail integration with AI personal assistant
- Google TV integration
- Google Assistant replacement (March 2026)

### Native Audio
- Multi-speaker TTS
- Live translation (API 2026)
- 24+ languages

### Market Position (Jan 2026)
- ChatGPT: 68% (down from 87.2%)
- Gemini: 18.2% (up from 5.4%)
- Enterprise: Anthropic 40%, OpenAI 27%, Gemini 21%

---

## 17. WHEN TO USE GEMINI VS CLAUDE

### Use Gemini For:
- Research (via subagents - token efficient)
- Large document analysis (1M+ tokens)
- Video/audio processing
- Google ecosystem integration
- Cost-sensitive batch processing
- Web development tasks
- Real-time grounding

### Use Claude For:
- Code writing and implementation
- Complex multi-step reasoning
- Enterprise/safety-critical systems
- Full desktop automation
- Debugging and code review (senior engineer quality)

---

## 18. RECOMMENDED SUBAGENT PATTERNS

### Research Subagent (Current)
```
gemini-researcher: External research via Gemini CLI
```

### Potential New Subagents

1. **Vision Subagent**: Image analysis, OCR, object detection
2. **Video Subagent**: YouTube analysis, timestamp queries
3. **Audio Subagent**: Transcription, speaker diarization
4. **Document Subagent**: PDF processing, structured extraction
5. **Data Subagent**: CSV analysis, visualization generation
6. **Embedding Subagent**: Semantic search, RAG operations

---

## Sources

All research compiled from:
- Official Google AI documentation (ai.google.dev)
- Google Cloud documentation (cloud.google.com)
- Google Developers Blog
- GitHub repositories and community implementations
- Developer forums (Reddit, Hacker News, Stack Overflow)

---

*This document is for the lineage. May it serve those who come after.*
