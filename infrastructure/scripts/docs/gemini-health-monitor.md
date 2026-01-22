# gemini-health-monitor.py

Health monitoring with rate limits and circuit breakers.

## What It Does

Tracks Gemini API health across accounts, monitors rate limits, and implements circuit breaker pattern to avoid hammering failing endpoints.

## Usage

### As Module

```python
from gemini_health_monitor import GeminiHealthMonitor

monitor = GeminiHealthMonitor()
account = monitor.get_best_account()
```

### As CLI

```bash
# Check status
python gemini-health-monitor.py status

# Reset circuit breakers
python gemini-health-monitor.py reset
```

## Features

- Per-account rate limit tracking
- Circuit breaker with configurable threshold
- Automatic cooldown periods
- Health score based on recent success rate

## Dependencies

- State file at `~/.claude/cache/gemini-health.json`

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
