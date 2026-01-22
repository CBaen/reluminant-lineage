# ollama-warmup.ps1

Pre-load embedding model on startup.

## What It Does

Warms up the Ollama embedding model by making an initial embedding request. Eliminates cold-start delay for the first real embedding request.

## Usage

```powershell
.\ollama-warmup.ps1
```

## Why Warmup?

First embedding request after Ollama starts can take 5-10 seconds as the model loads into memory. Warmup moves this delay to startup time.

## Model Warmed

`nomic-embed-text` - The embedding model used for all Qdrant operations.

## Dependencies

- PowerShell
- Ollama running

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
