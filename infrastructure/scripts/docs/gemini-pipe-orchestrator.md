# gemini-pipe-orchestrator.py

PowerShell-based Gemini execution for Windows.

## What It Does

Solves Windows pipe issues by using PowerShell directly instead of Git Bash. Provides reliable subprocess execution for Gemini calls on Windows systems.

## Usage

```python
from gemini_pipe_orchestrator import run_gemini_subprocess

success, data, stderr = run_gemini_subprocess(account=1, prompt="query")
```

## Function Signature

```python
def run_gemini_subprocess(
    account: int,
    prompt: str,
    model: str = "gemini-2.5-pro",
    timeout: int = 120
) -> Tuple[bool, dict, str]:
    """
    Returns:
        success: True if call succeeded
        data: Parsed JSON response or error dict
        stderr: Any stderr output
    """
```

## Why PowerShell?

Git Bash on Windows has issues with:
- Pipe buffering
- Signal handling
- Process termination

PowerShell provides native Windows process management.

## Dependencies

- PowerShell (built into Windows)
- `google-generativeai` SDK

## Changelog

- 2026-01-22: Fix PowerShell execution (276767f)
- 2026-01-20: Fix PowerShell compatibility and robustness (efd7851)
- 2026-01-20: Initial creation with conversation indexer (59ef471)
- 2026-01-19: Initial consolidation into repo (39a41dc)
