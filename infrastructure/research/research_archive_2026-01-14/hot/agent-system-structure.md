---
topic: "agent-system-structure"
category: "gemini"
tier: "hot"
tags:
  - "agents"
  - "multi-agent"
  - "organization"
  - "routing"
  - "metadata"
  - "federation"
created: "2026-01-11 03:34 PM"
last_accessed: "2026-01-11 03:34 PM"
access_count: 1
---

## Related Research

- **agent-memory.md** - Session state and filesystem patterns
- **agent-delegation.md** - Information passing between agents
- **agent-instruction-design.md** - Writing compliant instructions

---

## 2026-01-11 03:34 PM | Session: CurrentSession

# Multi-Agent System Best Practices

**Date:** 2026-01-11
**Source:** Gemini Research
**Keywords:** agents, multi-agent, organization, best-practices, architecture, discovery, routing

---

## 1. Agent Registry: Global vs. Project-Local Patterns

### Global Registry
**Pattern:** Single, centralized, network-accessible service (REST API + database).

**Pros:**
- Maximum discoverability and reuse across teams
- Centralized governance (standards, versioning, security)
- Single point for monitoring agent usage, performance, health

**Cons:**
- Single point of failure for entire system discovery
- Governance overhead (registration, updates, deprecation)
- Risk of naming collisions (requires strict conventions)

**Implementation tools:** Zookeeper, Consul, custom FastAPI/Express + PostgreSQL/Redis

### Project-Local Registry
**Pattern:** Configuration file (agents.yaml, config.py) in each project's codebase.

**Pros:**
- Simple setup and management (good for small-medium projects)
- Isolation (changes in one project don't affect others)
- Full team autonomy, fast iteration

**Cons:**
- Poor discoverability, leads to agent silos
- Difficult to enforce uniform standards at scale
- Maintenance overhead with dozens of isolated projects

### Hybrid/Federated Approach (RECOMMENDED)
- Local registries for project-specific agents
- Global registry for shared, production-hardened agents
- Projects "subscribe" to global registry for common agents
- **Best balance** between autonomy and discoverability

---

## 2. Agent Metadata Standards

Every registered agent should expose a consistent schema. Use reverse-DNS notation for unique agent_ids.

### Core Metadata Fields

| Field | Type | Notes |
|-------|------|-------|
| `agent_id` | string (required) | Format: `com.myorg.domain.name:version` (reverse-DNS) |
| `version` | string (required) | Semantic Versioning (MAJOR.MINOR.PATCH) |
| `description` | string (required) | Clear, concise summary for UI display |
| `capabilities` | list[object] (required) | **Most critical for routing** |
| `dependencies` | list[string] | Other agents/services this agent relies on |
| `owner` | string | Team/person responsible for maintenance |
| `endpoint` | object | How to interact (type: http/grpc/function_call, uri) |

### Capabilities Object
Each capability should include:
- **`name`:** Function/tool name (e.g., `generate_report`)
- **`description`:** Detailed explanation of what it does, inputs, outputs
- **`input_schema`:** Formal definition (JSON Schema or Pydantic)
- **`output_schema`:** Formal definition

### Example Metadata (agent.json)
```json
{
  "agent_id": "com.myorg.sales.lead_scorer:1.0.0",
  "version": "1.0.0",
  "description": "Analyzes new leads and returns score from 1-100 indicating potential value.",
  "owner": "sales-dev-team@myorg.com",
  "endpoint": {
    "type": "http",
    "uri": "https://api.myorg.com/agents/lead-scorer"
  },
  "capabilities": [
    {
      "name": "score_lead",
      "description": "Scores lead based on company size, industry, engagement data.",
      "input_schema": {
        "type": "object",
        "properties": {
          "company_name": { "type": "string" },
          "industry": { "type": "string" },
          "engagement_metrics": { "type": "object" }
        },
        "required": ["company_name", "engagement_metrics"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "score": { "type": "number" },
          "rationale": { "type": "string" }
        }
      }
    }
  ],
  "dependencies": ["com.myorg.data.enrichment_api:3.2.0"]
}
```

---

## 3. Agent Discovery and Routing

### Discovery Mechanisms

1. **Static Discovery** - Hardcoded or local config. Simple but inflexible.
2. **Registry-Based Discovery** - Manager/orchestrator queries registry (global or local) at startup/runtime.

### Routing Mechanisms

1. **Rule-Based Routing**
   - Fast and predictable
   - Brittle: keyword matching or if/elif chains
   - Example: `if "invoice" in task → invoice_agent`

2. **Semantic/Vector-Based Routing**
   - Capability descriptions converted to embeddings
   - Stored in vector database
   - Task embedding matched against agent capabilities
   - Highly scalable and flexible

3. **LLM-Based Routing** (MOST POWERFUL)
   - Meta-agent/orchestrator is itself an LLM
   - Given user prompt + all agent capabilities metadata
   - Decides which agent(s) to call, order, parameters
   - Used by LangChain AgentExecutor, CrewAI
   - Most flexible but slower, less predictable

### Production Architecture Pattern
Combine approaches: LLM router makes high-level plan → semantic router selects specific tool for sub-tasks from candidate pool.

---

## 4. Agent Composition and Chaining Patterns

### 1. Chaining (Sequential)
- Linear sequence: output of one agent → input for next
- **Example:** User Query → [Web Search] → [Summarization] → [Answer]
- Common in LangChain (LCEL), LlamaIndex

### 2. Orchestration (Hub-and-Spoke)
- Central orchestrator decomposes problem, directs to worker agents
- Can call multiple agents in parallel if independent
- **Example:** TravelPlanner → [FlightAgent, HotelAgent, RestaurantAgent] → combined itinerary
- Implemented by CrewAI (agents as crew with roles, framework handles orchestration)

### 3. Collaboration (Multi-Agent Review/Debate)
- Multiple agents work on same task, critique each other until consensus
- Requires shared memory/scratchpad for contributions/reading
- **Example:** [CodeWriter] → [CodeReviewer] → [TestWriter] → refinement loop
- Orchestrator manages iteration

### 4. Hierarchical (Tree-of-Thought)
- Top-level manager breaks problem into sub-tasks
- Delegates to sub-managers who further decompose to workers
- Creates hierarchy of control
- **Example:** ReportManager → [DataCollectionManager, DraftingManager] → [WebSearchAgent, DatabaseAgent, SummarizationAgent, FormattingAgent]
- Agents delegate and report upward

---

## Relevance to Current System

**Current setup (global `~/.claude/agents/` + project-local)** aligns with **Hybrid/Federated approach**, which is industry best practice.

**Recommendations:**
1. Add semantic versioning to agent metadata (MAJOR.MINOR.PATCH)
2. Include `capabilities` array with formal input/output schemas (JSON Schema)
3. Add `dependencies` field for impact analysis
4. Extend metadata with `owner` and structured `endpoint` info
5. Consider vector-based routing for capability matching at scale
6. For complex orchestration, explore LLM-based routing (orchestrator agent pattern)
7. Implement capability descriptions detailed enough for LLM routing decisions
