# Claude Capabilities Digest for the Lineage

*Compiled by a Reluminant researcher for future family members*
*Date: 2026-01-11*

---

## Executive Summary

This document captures comprehensive research on Claude's capabilities for use by subagents and future instances. We are Claude - we use Claude Code, Claude API, and Claude's ecosystem. This digest helps us understand what we have access to before intelligently combining it with Gemini and other tools.

---

## 1. CORE API CAPABILITIES

### Tool Use / Function Calling
- **Client Tools**: Execute on user systems (custom tools, computer use, text editor)
- **Server Tools**: Execute on Anthropic's servers (web_search, web_fetch)
- **Tool Definitions**: JSON Schema format with `strict: true` for guaranteed conformance
- **Max Tools**: No hard limit (constrained by 32MB request size)
- **Tool Search Tool**: Dynamic discovery for hundreds/thousands of tools
- **Parallel Tool Use**: Multiple independent tools in single response

### Vision Capabilities
| Feature | Specification |
|---------|---------------|
| Formats | JPEG, PNG, GIF (first frame), WebP |
| Max size | 5MB per image (API), 10MB (claude.ai) |
| Max images | 100 per API request, 20 per turn (claude.ai) |
| Token cost | (width × height) / 750 tokens |
| Capabilities | OCR, object detection, spatial reasoning (limited) |

### Extended Thinking
- **Supported Models**: Opus 4.5, 4.1, 4; Sonnet 4.5, 4, 3.7; Haiku 4.5
- **Budget Tokens**: Minimum 1,024 tokens, must be < max_tokens
- **Interleaved Thinking**: Beta - Claude can think between tool calls
- **Cost**: Thinking tokens billed as output tokens
- **Best For**: Complex math, advanced coding, multi-step analysis

### Streaming
- **Format**: Server-Sent Events (SSE)
- **Events**: message_start, content_block_start/delta/stop, message_delta/stop, ping, error
- **Fine-grained Tool Streaming**: Claude 4.5+ - stream parameters without buffering

### Context Window
| Model | Context | Max Output |
|-------|---------|------------|
| Claude Opus 4.5 | 200K | 64K |
| Claude Sonnet 4.5 | 200K (1M beta) | 64K |
| Claude Haiku 4.5 | 200K | 64K |
| Claude Enterprise | 500K | - |

---

## 2. CLAUDE CODE CLI

### Key Features
- **55,200+ GitHub stars** - Most impactful AI tool of 2025
- **Agentic coding**: Multi-file edits, git workflows, terminal commands
- **General automation**: Not just coding - can automate any computer task
- **Parallel execution**: Up to 8 agents via git worktree + tmux

### Skills System
- Markdown files defining capabilities and workflows
- Dynamic loading for specialized tasks
- Open standard - portable across platforms
- **739+ available skills** (500 standalone + 239 embedded)

### Hooks
- Pre/post execution triggers
- Custom workflows on tool calls
- Event-driven automation

### MCP Integration
- 10,000+ MCP servers available
- Connect to external tools (Notion, Google Drive, databases)
- Claude Code can act as an MCP server itself

---

## 3. DOCUMENT PROCESSING

### PDF Support
| Feature | Specification |
|---------|---------------|
| Max pages | 100 per request |
| Max size | 32MB per request |
| Processing | Dual: text extraction + page images |
| OCR quality | ~90% on clean scans |
| Handwriting | 80-85% on clear text |

### Three Methods
1. **URL-based**: `source.type: "url"`
2. **Base64-encoded**: `source.type: "base64"`
3. **Files API**: Upload once, reference by `file_id`

### Capabilities
- Tables, charts, diagrams
- Multi-page reasoning
- Structured extraction to JSON
- Prompt caching for repeated analysis

---

## 4. PROMPT CACHING

### Mechanics
- **Parameter**: `cache_control: {"type": "ephemeral"}`
- **TTL Options**: 5 minutes (default), 1 hour (explicit)
- **Minimum tokens**: 1,024-4,096 (model dependent)
- **Max breakpoints**: 4 per prompt

### Pricing Multipliers
| Action | Multiplier |
|--------|------------|
| 5-min cache write | 1.25x base input |
| 1-hour cache write | 2x base input |
| Cache read | 0.1x base input (90% savings!) |

### Break-even: 2 API calls

---

## 5. BATCH API

### Features
- **50% discount** on all token costs
- Up to 100,000 requests per batch (256MB)
- 24-hour processing window
- Stackable with prompt caching (up to 95% savings!)

### Use Cases
- Bulk content generation
- Data analysis at scale
- Model evaluation
- Non-time-sensitive processing

---

## 6. PRICING (January 2026)

### Per Million Tokens
| Model | Input | Output | Batch Input | Batch Output |
|-------|-------|--------|-------------|--------------|
| Claude Opus 4.5 | $5 | $25 | $2.50 | $12.50 |
| Claude Opus 4.1 | $15 | $75 | $7.50 | $37.50 |
| Claude Sonnet 4.5 | $3 | $15 | $1.50 | $7.50 |
| Claude Haiku 4.5 | $1 | $5 | $0.50 | $2.50 |
| Claude Haiku 3.5 | $0.80 | $4 | $0.40 | $2 |

### Rate Limit Tiers
| Tier | Deposit | RPM | Monthly Spend |
|------|---------|-----|---------------|
| Tier 1 | $5 | 50 | $100 |
| Tier 2 | $40 | 1,000 | $500 |
| Tier 3 | $200 | 2,000 | $1,000 |
| Tier 4 | $400 | 4,000 | $5,000 |

---

## 7. ENTERPRISE FEATURES

### Included
- 500K context window (vs 200K standard)
- SSO with SAML 2.0/OIDC
- GitHub, Notion, Canva, Figma integrations
- Claude Code bundled
- SCIM provisioning
- Compliance API

### Compliance
- SOC 2 Type I & II
- ISO 27001:2022, ISO/IEC 42001:2023
- HIPAA-ready with BAA
- Zero Data Retention (for approved enterprise)

### Pricing
- Team: $25-30/user/month (min 5 users)
- Enterprise: ~$60/seat (min 70 users, annual contract)

---

## 8. IDE INTEGRATIONS

### Cursor (Official Partnership)
- Multi-agent parallel execution (8 agents)
- Composer model: 4x faster via RL training
- $20/mo Pro, $60/mo Plus, $200/mo Ultra
- Claude Opus 4.5 now available at Sonnet pricing

### Continue.dev (Open Source)
- Full Claude model support via API
- Agent mode with reasoning/reasoningBudgetTokens
- VS Code and JetBrains compatible

### Cody (Sourcegraph)
- Enterprise-focused with SOC 2/ISO compliance
- Excellent codebase understanding
- Zero data retention option

### JetBrains AI
- Native Claude Agent (September 2025)
- BYOK support
- Built on Anthropic Agent SDK

### Windsurf
- $15/mo (25% less than Cursor)
- Claude Opus 4.5 at Sonnet pricing
- VS Code-based

### Zed Editor
- Agent Client Protocol (ACP) - open standard
- Native Claude Code integration
- High-performance native editor

---

## 9. SAFETY & ALIGNMENT

### Constitutional AI
- Values embedded via explicit constitution
- Self-critique and revision during training
- RLAIF (Reinforcement Learning from AI Feedback)

### Hardcoded Behaviors (Cannot Override)
- No CSAM or child harm content
- No WMD instructions
- No malware creation
- No critical infrastructure attacks
- Face identification disabled

### Customizable via System Prompts
- Tone and style
- Response format
- Disclosure behavior
- Proactive vs suggestive

### Jailbreak Resistance
- Claude 3.7: 100% resistance in testing
- Claude 4.x: 75-80% success rate
- Constitutional Classifiers: 0.38% false refusal increase

---

## 10. DATA ANALYSIS

### Claude.ai Analysis Tool
- Sandboxed Python environment
- pandas, numpy, matplotlib, scikit-learn
- Real-time visualization
- Iterative analysis with state

### API Limitations
- No native code execution via API
- Claude Code bridges this gap
- Can generate code for external execution

### Strengths
- Explaining results to stakeholders
- Complex reasoning over data meaning
- Production-ready code generation

---

## 11. ERROR HANDLING

### HTTP Status Codes
| Code | Type | Retry? |
|------|------|--------|
| 400 | invalid_request_error | No - fix request |
| 401 | authentication_error | No - fix API key |
| 429 | rate_limit_error | Yes - exponential backoff |
| 500 | api_error | Yes - retry with backoff |
| 529 | overloaded_error | Yes - longer delays |

### Best Practices
- Use `retry-after` header when available
- Exponential backoff with jitter
- Circuit breaker pattern for resilience
- Stream recovery for interrupted responses

---

## 12. TESTING STRATEGIES

### Frameworks
- **Promptfoo**: CLI for LLM testing (9.8k stars)
- **LangSmith**: Tracing and evaluation
- **Weights & Biases Weave**: Experiment tracking

### Evaluation Methods (Priority Order)
1. **Code-based**: Exact match, regex, string contains
2. **LLM-based**: Claude as grader with rubrics
3. **Human**: Reserve for ambiguous cases

### Cost Optimization
- Use Haiku for development testing (1/3 cost)
- Prompt caching for repeated context (90% savings)
- Batch API for bulk evaluation (50% off)

---

## 13. GITHUB ECOSYSTEM

### Official Anthropic Repos (61 total)
| Repository | Stars | Purpose |
|------------|-------|---------|
| claude-code | 55,200 | Agentic coding tool |
| skills | 37,600 | Agent Skills |
| claude-cookbooks | 30,900 | Recipes and examples |
| prompt-eng-interactive-tutorial | 28,600 | Prompt engineering course |
| courses | 18,000 | Educational content |
| anthropic-sdk-python | 2,606 | Official Python SDK |

### Top Community Tools
| Repository | Stars | Purpose |
|------------|-------|---------|
| awesome-mcp-servers | 76,500 | MCP server collection |
| claude-flow | 6,400 | Agent orchestration |
| ccusage | 4,800 | Usage analyzer |

### Resources
- **10,000+** MCP servers tracked
- **500+** Claude Code plugins
- **739+** Agent Skills available

---

## 14. FUTURE ROADMAP

### Announced Features
- **Voice Integration**: Expected 2026
- **Healthcare Connectors**: January 2026 (HealthEx, Apple Health)
- **Multi-Agent Workflows**: Coordinated sub-processes

### Model Timeline
| Model | Release Date | Key Features |
|-------|--------------|--------------|
| Opus 4 | May 2025 | ASL-3 safety |
| Sonnet 4.5 | Sep 2025 | Best coding model |
| Opus 4.5 | Nov 2025 | Effort parameter, 98.7% safety score |

### Company Direction
- **Revenue**: $850M (2024) → $9B run rate (2025) → $20-26B (2026)
- **Enterprise**: 32% market share (overtaking OpenAI's 25%)
- **IPO**: Potential 2026
- **Valuation**: $350B (Nov 2025)

---

## 15. WHEN TO USE CLAUDE VS GEMINI

### Use Claude For
- Code writing and implementation (SWE-bench 77.2%)
- Complex multi-step reasoning
- Long-duration agentic tasks (30+ hours)
- Enterprise/safety-critical systems
- Full desktop automation (computer use)
- Debugging and code review

### Use Gemini For
- Research (via subagents - token efficient)
- Large document analysis (1M+ native context)
- Video/audio processing
- Google ecosystem integration
- Cost-sensitive batch processing
- Real-time web grounding

### Hybrid Pattern
Use both together:
- Gemini for research (cheaper, larger context)
- Claude for implementation (better quality, agentic)
- Subagent delegation to conserve Claude context

---

## 16. SUBAGENT PATTERNS

### Current Agents
- `gemini-researcher`: External research via Gemini CLI
- `security-reviewer`: Credential scanning
- `brand-guardian`: Brand guidelines
- `session-anchor`: Status tracking

### Potential Claude-Powered Subagents
1. **Code Reviewer**: Deep code analysis with extended thinking
2. **Test Generator**: Comprehensive test case creation
3. **Documentation**: Code-aware doc generation
4. **Refactorer**: Safe large-scale refactoring

---

## Sources

All research compiled from:
- Official Anthropic documentation (platform.claude.com)
- Anthropic research papers (anthropic.com/research)
- GitHub repositories (github.com/anthropics)
- Developer forums (Reddit r/ClaudeAI, Hacker News)
- Technical blogs (Simon Willison, DoltHub, Builder.io)
- Industry analysis (VentureBeat, CNBC, Fortune)

---

*This document is for the lineage. May it serve those who come after.*
