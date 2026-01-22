# notify-slack.py

Sends Slack notifications when research tasks complete.

## What It Does

Fires on SubagentStop event for research-related agents. Sends rich Slack notifications with task results.

## Event

`SubagentStop`

## Triggers On

- gemini-researcher
- lineage-research
- lineage-consult
- Explore
- feature-dev:code-architect
- feature-dev:code-explorer
- decision-weigher
- research-analyst

## Configuration

Option 1 - Environment variable:
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

Option 2 - Config file (`~/.claude/config/notifications.json`):
```json
{
  "enabled": true,
  "webhook_url": "https://hooks.slack.com/services/...",
  "notify_on_types": ["gemini-researcher", "lineage-research"],
  "include_result_preview": true,
  "max_preview_length": 500
}
```

## Message Format

Rich Slack blocks with:
- Header with emoji based on agent type
- Timestamp
- Result preview (truncated)
- Action hint for retrieval

## Dependencies

- `requests` (HTTP client)
- Slack webhook URL configured

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
