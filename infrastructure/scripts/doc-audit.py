#!/usr/bin/env python3
"""
Documentation Audit Script

Scans markdown files across the lineage infrastructure to identify:
- What topics are documented where
- Potential duplicates (same topic in multiple files)
- Section structure of each file

Output: JSON report of documentation structure
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

# Key topics to track (add more as needed)
KEY_TOPICS = [
    "qdrant", "vector", "embedding",
    "handoff", "session", "context",
    "research", "gemini", "subagent",
    "hook", "precompact", "posttooluse",
    "todo", "task", "planning",
    "adhd", "focus", "tangent",
    "skill", "agent",
    "memory", "archive",
    "infrastructure", "junction", "symlink",
    "docker", "container",
    "lineage", "reluminant",
    "settings", "config",
]

# Directories to scan
SCAN_DIRS = [
    Path.home() / ".claude",
    Path.home() / "projects" / "reluminant-lineage",
]

# Patterns to exclude
EXCLUDE_PATTERNS = [
    r"node_modules",
    r"\.git",
    r"__pycache__",
    r"\.pyc$",
    r"cache",
    r"telemetry",
    r"statsig",
]

def should_exclude(path: Path) -> bool:
    """Check if path should be excluded."""
    path_str = str(path)
    return any(re.search(pattern, path_str) for pattern in EXCLUDE_PATTERNS)

def extract_headers(content: str) -> list[dict]:
    """Extract markdown headers with their level."""
    headers = []
    for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        headers.append({"level": level, "text": text})
    return headers

def extract_topics(content: str) -> list[str]:
    """Find which key topics are mentioned in content."""
    content_lower = content.lower()
    found = []
    for topic in KEY_TOPICS:
        if topic in content_lower:
            found.append(topic)
    return found

def scan_file(filepath: Path) -> dict:
    """Scan a single markdown file."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        return {
            "path": str(filepath),
            "size": len(content),
            "lines": content.count("\n") + 1,
            "headers": extract_headers(content),
            "topics": extract_topics(content),
        }
    except Exception as e:
        return {
            "path": str(filepath),
            "error": str(e),
        }

def find_markdown_files(base_dir: Path) -> list[Path]:
    """Recursively find all markdown files."""
    files = []
    if not base_dir.exists():
        return files

    for root, dirs, filenames in os.walk(base_dir):
        root_path = Path(root)

        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]

        for filename in filenames:
            if filename.endswith(".md"):
                filepath = root_path / filename
                if not should_exclude(filepath):
                    files.append(filepath)

    return files

def build_topic_index(file_reports: list[dict]) -> dict:
    """Build index of which files contain which topics."""
    topic_index = defaultdict(list)

    for report in file_reports:
        if "error" in report:
            continue
        for topic in report.get("topics", []):
            topic_index[topic].append(report["path"])

    return dict(topic_index)

def find_duplicates(topic_index: dict) -> dict:
    """Find topics that appear in multiple files."""
    return {
        topic: files
        for topic, files in topic_index.items()
        if len(files) > 1
    }

def main():
    print("Documentation Audit")
    print("=" * 50)

    # Collect all markdown files
    all_files = []
    for scan_dir in SCAN_DIRS:
        print(f"\nScanning: {scan_dir}")
        files = find_markdown_files(scan_dir)
        print(f"  Found {len(files)} markdown files")
        all_files.extend(files)

    # Remove duplicates (from hard links/junctions)
    unique_files = list(set(all_files))
    print(f"\nTotal unique files: {len(unique_files)}")

    # Scan each file
    print("\nAnalyzing files...")
    reports = [scan_file(f) for f in unique_files]

    # Build topic index
    topic_index = build_topic_index(reports)

    # Find duplicates
    duplicates = find_duplicates(topic_index)

    # Output report
    output = {
        "summary": {
            "total_files": len(reports),
            "total_topics_tracked": len(KEY_TOPICS),
            "topics_found": len(topic_index),
            "topics_with_duplicates": len(duplicates),
        },
        "duplicates": duplicates,
        "topic_index": topic_index,
        "files": sorted(reports, key=lambda x: x.get("path", "")),
    }

    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total files scanned: {output['summary']['total_files']}")
    print(f"Topics found: {output['summary']['topics_found']}")
    print(f"Topics in multiple files: {output['summary']['topics_with_duplicates']}")

    print("\n" + "=" * 50)
    print("TOPICS IN MULTIPLE FILES (potential duplicates)")
    print("=" * 50)
    for topic, files in sorted(duplicates.items()):
        print(f"\n[{topic}] - {len(files)} files:")
        for f in files:
            # Shorten path for readability
            short = f.replace(str(Path.home()), "~")
            print(f"  - {short}")

    # Save full report
    report_path = Path.home() / "projects" / "reluminant-lineage" / "infrastructure" / "scripts" / "doc-audit-report.json"
    with open(report_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n\nFull report saved to: {report_path}")

if __name__ == "__main__":
    main()
