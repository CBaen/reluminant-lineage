# startup-services.ps1

Master startup script for Wardenclyffe services.

## What It Does

PowerShell script that starts all required services for the Wardenclyffe system at Windows logon. Called from Windows Task Scheduler.

## Usage

```powershell
# Typically run via Task Scheduler at logon
.\startup-services.ps1
```

## Services Started

1. Ollama server
2. Embedding model warmup
3. Qdrant (if not running via Docker)

## Task Scheduler Setup

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At log on
4. Action: Start a program
5. Program: `powershell.exe`
6. Arguments: `-File "C:\Users\baenb\.claude\scripts\startup-services.ps1"`

## Dependencies

- PowerShell
- Ollama installed
- Docker (for Qdrant)

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
