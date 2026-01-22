# Changelog

All notable changes to hooks will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.1.0] - 2026-01-22

### Added

- changelog-reminder.sh: Reminds to update CHANGELOG.md when infrastructure/ files are modified

## [1.0.0] - 2026-01-22

### Added

- session-end-handoff.py: Queues transcripts for async Qdrant storage
- handoff-worker.py: Processes queued transcripts with Gemini
- notify-slack.py: Sends Slack notifications for research completion
- auto-commit.sh: Auto-commits file changes (registered in settings.json)
- docs/ folder with documentation for each hook
