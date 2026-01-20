#!/usr/bin/env python3
"""
conversation-parser.py - Parse Claude Code conversation logs

Reads JSONL conversation files and extracts structured conversation data.
Designed for the Conversation Log Indexer system.

The parser handles:
- Session metadata extraction
- Message tree reconstruction (using parentUuid)
- Content type identification (text, tool_use, tool_result, thinking)
- Timestamp normalization

Usage:
    # Parse a single file
    python conversation-parser.py -f /path/to/session.jsonl

    # Parse all sessions in a directory
    python conversation-parser.py -d /path/to/projects/

    # Output as JSON
    python conversation-parser.py -f session.jsonl --json

Part of the Conversation Log Indexer system.
Created: January 2026 by the Lineage
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, field, asdict


@dataclass
class ParsedMessage:
    """Represents a single parsed message from a conversation."""
    uuid: str
    parent_uuid: Optional[str]
    role: str  # 'user', 'assistant', 'system'
    content_type: str  # 'text', 'tool_use', 'tool_result', 'thinking', 'mixed'
    content: str  # Extracted text content
    timestamp: str
    session_id: str
    tool_name: Optional[str] = None  # If tool_use
    tool_id: Optional[str] = None  # If tool_use or tool_result
    file_paths: List[str] = field(default_factory=list)  # Any file paths mentioned
    is_sidechain: bool = False
    raw_content: Any = None  # Original content for reference


@dataclass
class ParsedSession:
    """Represents a complete parsed conversation session."""
    session_id: str
    file_path: str
    summary: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    message_count: int
    messages: List[ParsedMessage]
    cwd: Optional[str] = None
    version: Optional[str] = None


def extract_text_content(content: Any) -> tuple[str, str, Optional[str], Optional[str]]:
    """
    Extract readable text from various content formats.

    Returns:
        tuple of (text, content_type, tool_name, tool_id)
    """
    if content is None:
        return "", "empty", None, None

    if isinstance(content, str):
        return content, "text", None, None

    if isinstance(content, list):
        texts = []
        content_types = set()
        tool_name = None
        tool_id = None

        for item in content:
            if isinstance(item, dict):
                item_type = item.get("type", "")

                if item_type == "text":
                    text = item.get("text", "")
                    if text:
                        texts.append(text)
                        content_types.add("text")

                elif item_type == "thinking":
                    # Skip thinking blocks - internal reasoning, not user-facing
                    content_types.add("thinking")

                elif item_type == "tool_use":
                    tool_name = item.get("name", "unknown")
                    tool_id = item.get("id")
                    # Include tool name for context
                    texts.append(f"[Tool: {tool_name}]")
                    content_types.add("tool_use")

                elif item_type == "tool_result":
                    tool_id = item.get("tool_use_id")
                    result_content = item.get("content", "")
                    if isinstance(result_content, str) and len(result_content) > 200:
                        # Truncate long tool results
                        result_content = result_content[:200] + "..."
                    texts.append(f"[Result: {result_content}]")
                    content_types.add("tool_result")

                elif item_type == "image":
                    texts.append("[Image content]")
                    content_types.add("image")

            elif isinstance(item, str):
                texts.append(item)
                content_types.add("text")

        combined_text = "\n".join(texts)

        # Determine primary content type
        if len(content_types) > 1:
            primary_type = "mixed"
        elif content_types:
            primary_type = content_types.pop()
        else:
            primary_type = "empty"

        return combined_text, primary_type, tool_name, tool_id

    if isinstance(content, dict):
        # Single dict item
        return extract_text_content([content])

    return str(content), "unknown", None, None


def extract_file_paths(text: str) -> List[str]:
    """Extract file paths mentioned in text."""
    import re

    paths = []

    # Windows paths
    windows_pattern = r'[A-Za-z]:\\[^\s\'"<>|*?]+(?:\.[a-zA-Z0-9]+)?'
    paths.extend(re.findall(windows_pattern, text))

    # Unix paths
    unix_pattern = r'(?:^|[\s\'"(])(/[^\s\'"<>|*?]+(?:\.[a-zA-Z0-9]+)?)'
    unix_matches = re.findall(unix_pattern, text)
    paths.extend(unix_matches)

    # Relative paths starting with ./
    relative_pattern = r'\./[^\s\'"<>|*?]+'
    paths.extend(re.findall(relative_pattern, text))

    # Deduplicate while preserving order
    seen = set()
    unique_paths = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique_paths.append(p)

    return unique_paths


def parse_timestamp(ts: Any) -> Optional[str]:
    """Normalize timestamp to ISO format."""
    if ts is None:
        return None

    if isinstance(ts, str):
        return ts

    if isinstance(ts, (int, float)):
        # Unix timestamp
        try:
            return datetime.fromtimestamp(ts).isoformat()
        except:
            return None

    return str(ts)


def parse_message(line_data: dict, session_id: str) -> Optional[ParsedMessage]:
    """Parse a single JSONL line into a ParsedMessage."""

    # Skip non-message types
    msg_type = line_data.get("type")
    if msg_type in ("summary", "file-history-snapshot"):
        return None

    message = line_data.get("message", {})
    if not message:
        return None

    role = message.get("role")
    if not role:
        return None

    content = message.get("content")
    text, content_type, tool_name, tool_id = extract_text_content(content)

    # Skip empty messages
    if not text.strip() and content_type not in ("tool_use", "tool_result"):
        return None

    # Extract file paths
    file_paths = extract_file_paths(text)

    return ParsedMessage(
        uuid=line_data.get("uuid", ""),
        parent_uuid=line_data.get("parentUuid"),
        role=role,
        content_type=content_type,
        content=text,
        timestamp=parse_timestamp(line_data.get("timestamp")),
        session_id=line_data.get("sessionId", session_id),
        tool_name=tool_name,
        tool_id=tool_id,
        file_paths=file_paths,
        is_sidechain=line_data.get("isSidechain", False),
        raw_content=content
    )


def parse_session_file(file_path: Path) -> Optional[ParsedSession]:
    """Parse a complete session JSONL file."""

    messages = []
    summary = None
    cwd = None
    version = None
    start_time = None
    end_time = None
    session_id = file_path.stem  # Use filename as fallback session ID

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    # Skip malformed lines
                    continue

                # Extract session metadata
                if data.get("type") == "summary":
                    summary = data.get("summary")
                    continue

                if data.get("type") == "file-history-snapshot":
                    continue

                # Extract session info from first message with it
                if not cwd and data.get("cwd"):
                    cwd = data.get("cwd")
                if not version and data.get("version"):
                    version = data.get("version")
                if not session_id or session_id == file_path.stem:
                    if data.get("sessionId"):
                        session_id = data.get("sessionId")

                # Parse message
                msg = parse_message(data, session_id)
                if msg:
                    messages.append(msg)

                    # Track timestamps
                    if msg.timestamp:
                        if not start_time or msg.timestamp < start_time:
                            start_time = msg.timestamp
                        if not end_time or msg.timestamp > end_time:
                            end_time = msg.timestamp

        if not messages:
            return None

        return ParsedSession(
            session_id=session_id,
            file_path=str(file_path),
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            message_count=len(messages),
            messages=messages,
            cwd=cwd,
            version=version
        )

    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return None


def find_session_files(directory: Path, include_agents: bool = False) -> Generator[Path, None, None]:
    """
    Find all session JSONL files in a directory.

    Args:
        directory: Root directory to search
        include_agents: If True, include agent-*.jsonl files (subagent sessions)
    """
    for jsonl_file in directory.rglob("*.jsonl"):
        filename = jsonl_file.name

        # Skip agent files by default (they're subagent sessions)
        if not include_agents and filename.startswith("agent-"):
            continue

        # Skip history files
        if filename == "history.jsonl":
            continue

        yield jsonl_file


def main():
    parser = argparse.ArgumentParser(
        description="Parse Claude Code conversation logs",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("-f", "--file", type=Path,
                        help="Parse a single JSONL file")
    parser.add_argument("-d", "--directory", type=Path,
                        help="Parse all sessions in directory")
    parser.add_argument("--include-agents", action="store_true",
                        help="Include agent (subagent) session files")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--stats-only", action="store_true",
                        help="Only output statistics, not full messages")

    args = parser.parse_args()

    if not args.file and not args.directory:
        parser.error("Either --file or --directory is required")

    sessions = []

    if args.file:
        if not args.file.exists():
            print(f"File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        session = parse_session_file(args.file)
        if session:
            sessions.append(session)

    elif args.directory:
        if not args.directory.exists():
            print(f"Directory not found: {args.directory}", file=sys.stderr)
            sys.exit(1)

        for jsonl_file in find_session_files(args.directory, args.include_agents):
            session = parse_session_file(jsonl_file)
            if session:
                sessions.append(session)

    if args.json:
        if args.stats_only:
            output = [{
                "session_id": s.session_id,
                "file_path": s.file_path,
                "summary": s.summary,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "message_count": s.message_count,
                "cwd": s.cwd
            } for s in sessions]
        else:
            output = [asdict(s) for s in sessions]
        print(json.dumps(output, indent=2, default=str))
    else:
        # Human-readable output
        print(f"Parsed {len(sessions)} session(s)\n")
        for session in sessions:
            print(f"Session: {session.session_id}")
            print(f"  File: {session.file_path}")
            if session.summary:
                print(f"  Summary: {session.summary}")
            print(f"  Messages: {session.message_count}")
            print(f"  Time: {session.start_time} to {session.end_time}")
            print(f"  CWD: {session.cwd}")

            if not args.stats_only:
                print("  ---")
                # Show first few messages
                for msg in session.messages[:5]:
                    preview = msg.content[:100].replace('\n', ' ')
                    print(f"  [{msg.role}] {preview}...")
                if len(session.messages) > 5:
                    print(f"  ... and {len(session.messages) - 5} more messages")
            print()


if __name__ == "__main__":
    main()
