# Changelog

All notable changes to scripts will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.0.0] - 2026-01-22

### Added

- **Qdrant Operations** (11 scripts): qdrant-peek.py, qdrant-chunked-store.py, qdrant-semantic-search.py, and more
- **Gemini Integration** (11 scripts): gemini-account.sh, gemini-api-call.py, gemini-research-store.py, and more
- **Research Pipeline** (7 scripts): research-pipeline.sh, research-store.sh, research-supervisor.py, and more
- **Conversation Indexing** (4 scripts): conversation-indexer.py, conversation-parser.py, and more
- **Utilities** (12 scripts): fix-hard-links.py, extract-json.py, doc-audit.py, and more
- **System Startup** (2 scripts): startup-services.ps1, ollama-warmup.ps1
- docs/ folder with documentation for each script

### Deprecated

- qdrant-query.py, qdrant-query-v2.py: Use qdrant-semantic-search.py instead
- qdrant-store.py, qdrant-store.sh: Use qdrant-chunked-store.py instead
