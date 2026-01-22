# Changelog

All notable changes to the plugins marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.0.0] - 2026-01-22

### Added

- marketplace.json in .claude-plugin/ to enable local plugin marketplace
- lineage-powers plugin (see lineage-powers/CHANGELOG.md for plugin-specific changes)

### Notes

This folder serves as a local Claude Code marketplace. To add a new plugin:
1. Create a folder with the plugin name
2. Add .claude-plugin/plugin.json with metadata
3. Update .claude-plugin/marketplace.json to include the new plugin
