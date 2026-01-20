---
topic: "agent-error-handling"
category: "gemini"
tier: "hot"
tags:
  - "errors"
  - "retry"
  - "escalation"
  - "circuit-breaker"
  - "graceful-degradation"
created: "2026-01-11 04:32 PM"
last_accessed: "2026-01-11 04:32 PM"
access_count: 1
---

## 2026-01-11 04:32 PM | Session: Consolidator

# AI Agent Error Handling Patterns

Research Date: 2026-01-11
Source: Google Gemini

## 1. Failure Detection and Retry Logic

Automatic recovery from temporary failures is the foundation of resilient agents.

### Failure Detection
- Check HTTP status codes (e.g., 503 Service Unavailable)
- Look for exceptions in code execution
- Use timeouts for long-running operations

### Transient vs. Permanent Errors
**Transient errors** (retry candidates):
- Network timeouts
- Temporary API server overload
- Rate limiting (429)
- Temporary service unavailability (503)

**Permanent errors** (don't retry):
- Authentication failures (bad API key)
- Invalid input data
- Permission errors
- Logic bugs in code

### Exponential Backoff
Wait progressively longer between retries: 2s → 4s → 8s → 16s...

**Benefits**:
- Prevents overwhelming struggling services
- Reduces cascading failures
- Gives systems time to recover

### Jitter
Add small random delays to backoff times.

**Why**: Prevents thundering herd when multiple agents retry simultaneously.

**Example**: If exponential backoff says 4s, add ±0.5s randomness → 3.5-4.5s actual wait.

### Max Retries
Set absolute limit on retry attempts (e.g., 3-5 retries typically).

**Prevents**:
- Infinite loops
- Resource exhaustion
- Long wait times for users

---

## 2. Escalation Decision Trees

When retries fail, agents need decision logic for: escalate to user? Try alternative? Fail gracefully?

### Example Decision Tree

```
1. Is error permanent?
   ├─ YES → Escalate immediately (ask user to fix input/credentials)
   └─ NO → Proceed to step 2

2. Max retries reached?
   ├─ YES → Escalate (inform user, log for developers)
   └─ NO → Continue retrying

3. Alternative method available?
   ├─ YES → Try fallback tool/strategy
   └─ NO → Escalate
```

### Escalation Types

| Scenario | Action | Message |
|----------|--------|---------|
| Bad credentials/permissions | Ask user | "Please verify your API key and permissions" |
| Service degraded (503s after retries) | Inform + fail | "Service temporarily unavailable, please try again later" |
| Invalid input (permanent) | Ask user | "Input format invalid. Please provide..." |
| Transient still failing after max retries | Inform + log | Log error ID for operator debugging |
| Alternative path exists | Try fallback | Switch to backup API, reduced functionality, etc. |

---

## 3. Graceful Degradation Strategies

Continue operating with reduced functionality instead of complete failure.

### Fallback Modes
**Example**: Complex visualization fails → render as simple table instead.

**Pattern**:
1. Try primary feature
2. On failure, try reduced-complexity alternative
3. On that failure, provide minimal viable response
4. Always inform user of degradation

### Reduced Functionality
Temporarily disable non-essential features when parts fail.

**Example**:
- Article summarization service working ✓
- Image fetching service failing ✗
→ Provide summaries without images (user informed)

### Circuit Breakers
When an operation fails repeatedly, stop attempting it for a timeout period.

**Implementation**:
```
Failure Count Tracker:
  - Track consecutive failures for each operation
  - When count reaches threshold (e.g., 5):
    - "Trip" the circuit breaker
    - Stop attempting operation for X minutes
    - Periodically test if operation recovers
    - Resume normal operation when healthy

Benefits:
  - Prevents wasted time on broken services
  - Prevents cascading failures
  - Reduces load on failing systems
```

**States**:
- **CLOSED**: Operating normally
- **OPEN**: Stopped attempting (waiting for recovery)
- **HALF_OPEN**: Testing if service recovered

---

## 4. Error Reporting for Debugging

Detailed, structured error reports enable diagnosis and fixes.

### Structured Format (JSON)
```json
{
  "timestamp": "2026-01-11T14:32:00Z",
  "request_id": "req-xyz-789",
  "agent_id": "agent-summarizer-v2.1",
  "error_code": "EXTERNAL_SERVICE_TIMEOUT",
  "error_message": "API call to document-fetcher timed out after 30s",
  "severity": "high",
  "is_transient": true,
  "retry_count": 3,
  "context": {
    "original_user_request": "Summarize the article at https://example.com/article",
    "agent_task": "fetch_and_summarize",
    "agent_step": 2,
    "tool_used": "http_get_document",
    "input_data": {
      "url": "https://example.com/article",
      "timeout_ms": 30000
    }
  },
  "stack_trace": "...",
  "suggested_action": "Retry with exponential backoff"
}
```

### Context Preservation
Include everything needed to reproduce the issue:
- Original user request
- Agent's current task and plan
- Specific tool/function that failed
- Input data provided
- Full stack trace
- Sequence of steps before failure

### Debugging Metadata
- **Timestamp**: Precise time of error
- **Request ID**: Trace across distributed systems
- **Agent version**: What version had the bug?
- **Step sequence**: Breadcrumb trail of actions
- **Environment**: Which region/environment failed?

### Observability Integration
Send errors to monitoring platforms:
- **Datadog**: Real-time dashboards, alerting
- **Splunk**: Log aggregation and analysis
- **OpenTelemetry**: Language-agnostic observability
- **Custom logging**: ELK stack, CloudWatch, etc.

**Enable**:
- Error rate monitoring by error type
- Alerting on spike in transient errors
- Dashboards tracking agent health
- Historical trend analysis

---

## Key Principles Summary

1. **Differentiate transient from permanent errors** - Only retry on transients
2. **Use exponential backoff + jitter** - Reduces load, prevents thundering herd
3. **Set max retries** - Prevents infinite loops
4. **Escalate intelligently** - Ask user only when needed, fail gracefully otherwise
5. **Provide fallbacks** - Reduced functionality beats no functionality
6. **Use circuit breakers** - Stop hammering broken services
7. **Structure error reports** - JSON, with full context and metadata
8. **Integrate with observability** - Real-time monitoring and alerting
9. **Preserve debugging context** - Original request, steps taken, inputs
10. **Inform users gracefully** - Clear, actionable messages when things fail

---

## Design Patterns for Implementation

### Retry Wrapper
```
function retryWithBackoff(fn, maxRetries=3, backoffMs=1000):
  for attempt in 1..maxRetries:
    try:
      return fn()
    except TransientError as e:
      if attempt == maxRetries: raise
      waitTime = backoffMs * (2^(attempt-1)) + random(0, jitter)
      sleep(waitTime)
    except PermanentError as e:
      escalate(e)
```

### Escalation Router
```
function handleError(error, context):
  if isPermanent(error):
    askUser(error, context)
  elif hasAlternative(error):
    tryAlternative(context)
  elif shouldEscalate(error, retryCount):
    informUserAndLog(error, context)
  else:
    retry()
```

### Circuit Breaker State Machine
```
CLOSED → (failure threshold reached) → OPEN
OPEN → (timeout elapsed) → HALF_OPEN
HALF_OPEN → (test succeeds) → CLOSED
HALF_OPEN → (test fails) → OPEN
```
