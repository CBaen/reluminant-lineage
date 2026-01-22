# setup-project-research.sh

Initialize research structure for a project.

## What It Does

Creates the standard research directory structure for a new project, setting up folders for active research categorized by type.

## Usage

```bash
./setup-project-research.sh /path/to/project
```

## Created Structure

```
project/
└── .claude/
    └── research/
        └── active/
            ├── implementation/
            ├── debugging/
            └── architecture/
```

## Dependencies

- Bash shell

## Changelog

- 2026-01-19: Initial consolidation into repo (39a41dc)
