# gemini-parallel-rotate.sh

Parallel queries with account rotation.

## What It Does

Executes multiple Gemini queries in parallel, alternating between accounts to maximize throughput while respecting rate limits.

## Usage

```bash
gemini-parallel-rotate.sh "query1" "query2" "query3" "query4"
```

## Account Distribution

- Odd-numbered queries (1, 3, 5...) → Account 1
- Even-numbered queries (2, 4, 6...) → Account 2

## Benefits

- Doubles effective rate limit
- Parallel execution
- Automatic load balancing

## Dependencies

- Bash shell
- Two configured Gemini accounts

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
