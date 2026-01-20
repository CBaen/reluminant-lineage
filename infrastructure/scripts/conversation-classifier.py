#!/usr/bin/env python3
"""
conversation-classifier.py - Classify conversation segments for indexing

Takes parsed conversation messages and classifies them into:
- IMPORTANT: Decisions, file changes, errors, technical discussions, implementation
- SKIP: Greetings, short responses, housekeeping, routine tool outputs

Also groups related messages into logical "exchanges" for better summarization.

Usage:
    # Classify a parsed session (from JSON)
    cat parsed_session.json | python conversation-classifier.py

    # Directly from a JSONL file
    python conversation-classifier.py -f /path/to/session.jsonl

    # With threshold adjustment
    python conversation-classifier.py -f session.jsonl --min-length 30

Part of the Conversation Log Indexer system.
Created: January 2026 by the Lineage
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Add scripts directory for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


class Classification(Enum):
    """Classification categories for conversation content."""
    DECISION = "decision"           # Architecture/design decisions
    FILE_CHANGE = "file_change"     # Code modifications
    ERROR_FIX = "error_fix"         # Bug fixes, error resolution
    DISCUSSION = "discussion"       # Technical discussions
    IMPLEMENTATION = "implementation"  # Feature implementation
    RESEARCH = "research"           # Investigation, exploration
    CONFIGURATION = "configuration"  # Setup, config changes
    SKIP = "skip"                   # Not worth indexing


@dataclass
class ClassifiedExchange:
    """A group of related messages with classification."""
    exchange_id: str
    classification: str
    importance: str  # 'high', 'medium', 'low'
    messages: List[dict]  # List of ParsedMessage dicts
    summary_hint: str  # Brief description for summarizer
    file_paths: List[str]
    start_time: Optional[str]
    end_time: Optional[str]
    word_count: int
    keywords: List[str] = field(default_factory=list)


# Patterns for classification
SKIP_PATTERNS = [
    # Greetings and acknowledgments
    r'^(hi|hello|hey|thanks|thank you|ok|okay|sure|yes|no|got it)[\s!.,]*$',
    r'^(sounds good|perfect|great|awesome|nice|cool)[\s!.,]*$',
    # Session housekeeping
    r'<local-command-(stdout|caveat)>',
    r'^<command-name>/(context|help|clear|memory)',
    # Meta responses
    r'^(let me|i\'ll|i will|i am going to)(\s+\w+){0,3}\s*[.!]*$',
]

DECISION_PATTERNS = [
    r'(decide|decided|decision|choosing|chose|selected|picked)',
    r'(approach|strategy|architecture|design|pattern)',
    r'(better|prefer|recommend|suggestion)',
    r'(trade-?off|pros?\s+and\s+cons?|advantages?|disadvantages?)',
    r'(option\s*[a-d1-4]|alternative)',
]

ERROR_PATTERNS = [
    r'(error|exception|failed|failure|crash|bug)',
    r'(fix|fixed|fixing|resolved|resolved)',
    r'(issue|problem|trouble|wrong)',
    r'(traceback|stack\s*trace|undefined|null)',
    r'(debug|debugging|investigate|investigating)',
]

FILE_CHANGE_PATTERNS = [
    r'(edit|edited|modify|modified|change|changed)',
    r'(create|created|write|wrote|add|added)',
    r'(delete|deleted|remove|removed)',
    r'(refactor|refactored|reorganize|reorganized)',
    r'\[Tool:\s*(Edit|Write|NotebookEdit)\]',
]

IMPLEMENTATION_PATTERNS = [
    r'(implement|implemented|implementing|build|building)',
    r'(feature|functionality|capability)',
    r'(complete|completed|finish|finished|done)',
    r'(working|works|functional)',
]

RESEARCH_PATTERNS = [
    r'(research|researching|investigate|investigating)',
    r'(explore|exploring|search|searching)',
    r'(found|discovered|learned)',
    r'(understand|understanding|figure out)',
    r'\[Tool:\s*(Read|Glob|Grep|WebSearch|WebFetch)\]',
]


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def extract_keywords(text: str) -> List[str]:
    """Extract potential keywords from text."""
    # Remove tool markers and common punctuation
    clean = re.sub(r'\[Tool:\s*\w+\]', '', text)
    clean = re.sub(r'\[Result:[^\]]*\]', '', clean)
    clean = re.sub(r'[^\w\s-]', ' ', clean)

    words = clean.lower().split()

    # Filter for meaningful keywords (length > 3, not common words)
    stopwords = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
        'had', 'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been',
        'were', 'they', 'this', 'that', 'with', 'from', 'will', 'what',
        'when', 'which', 'their', 'there', 'would', 'could', 'should',
        'about', 'into', 'more', 'some', 'such', 'than', 'then', 'them',
        'these', 'those', 'only', 'just', 'also', 'very', 'being', 'your',
        'here', 'need', 'make', 'like', 'want', 'look', 'going', 'does',
        'file', 'files', 'tool', 'result', 'content', 'text', 'using'
    }

    keywords = []
    seen = set()
    for word in words:
        if len(word) > 3 and word not in stopwords and word not in seen:
            seen.add(word)
            keywords.append(word)
            if len(keywords) >= 10:
                break

    return keywords


def should_skip(message: dict, min_length: int = 50) -> bool:
    """Check if a message should be skipped."""
    content = message.get('content', '')

    # Skip short messages
    if len(content.strip()) < min_length:
        return True

    # Skip based on patterns
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True

    # Skip pure tool results with no context
    if message.get('content_type') == 'tool_result' and len(content) < 200:
        return True

    # Skip sidechain messages (usually debugging)
    if message.get('is_sidechain'):
        return True

    return False


def classify_content(text: str) -> Tuple[Classification, str]:
    """
    Classify content and return (classification, importance).

    Returns:
        Tuple of (Classification, importance_level)
    """
    text_lower = text.lower()

    # Check decision patterns (highest priority)
    for pattern in DECISION_PATTERNS:
        if re.search(pattern, text_lower):
            return Classification.DECISION, "high"

    # Check error/fix patterns
    for pattern in ERROR_PATTERNS:
        if re.search(pattern, text_lower):
            return Classification.ERROR_FIX, "high"

    # Check file change patterns
    for pattern in FILE_CHANGE_PATTERNS:
        if re.search(pattern, text_lower):
            return Classification.FILE_CHANGE, "medium"

    # Check implementation patterns
    for pattern in IMPLEMENTATION_PATTERNS:
        if re.search(pattern, text_lower):
            return Classification.IMPLEMENTATION, "medium"

    # Check research patterns
    for pattern in RESEARCH_PATTERNS:
        if re.search(pattern, text_lower):
            return Classification.RESEARCH, "low"

    # Default to discussion if substantial content
    if count_words(text) > 50:
        return Classification.DISCUSSION, "low"

    return Classification.SKIP, "low"


def group_into_exchanges(
    messages: List[dict],
    max_gap_messages: int = 5,
    min_messages: int = 2
) -> List[List[dict]]:
    """
    Group related messages into exchanges.

    An exchange is a coherent back-and-forth about a specific topic.
    We group based on:
    - Temporal proximity (parentUuid relationships)
    - Topic continuity (shared file paths, keywords)
    """
    if not messages:
        return []

    exchanges = []
    current_exchange = []

    for i, msg in enumerate(messages):
        if not current_exchange:
            current_exchange.append(msg)
            continue

        # Check if this message continues the exchange
        last_msg = current_exchange[-1]

        # Same topic indicators
        shares_files = bool(
            set(msg.get('file_paths', [])) &
            set(last_msg.get('file_paths', []))
        )

        # Check for parent-child relationship
        is_response = msg.get('parent_uuid') == last_msg.get('uuid')

        # Check temporal continuity (rough estimate)
        same_classification, _ = classify_content(msg.get('content', ''))
        last_classification, _ = classify_content(last_msg.get('content', ''))
        same_topic = same_classification == last_classification

        # Continue exchange if related
        if shares_files or is_response or (same_topic and len(current_exchange) < 10):
            current_exchange.append(msg)
        else:
            # Finalize current exchange if substantial
            if len(current_exchange) >= min_messages:
                exchanges.append(current_exchange)
            current_exchange = [msg]

    # Don't forget the last exchange
    if len(current_exchange) >= min_messages:
        exchanges.append(current_exchange)

    return exchanges


def classify_exchange(messages: List[dict]) -> ClassifiedExchange:
    """Classify a group of messages as an exchange."""
    import uuid as uuid_module

    # Combine content for classification
    all_content = " ".join(m.get('content', '') for m in messages)
    classification, importance = classify_content(all_content)

    # Collect file paths
    all_paths = []
    for m in messages:
        all_paths.extend(m.get('file_paths', []))
    unique_paths = list(dict.fromkeys(all_paths))  # Preserve order, dedupe

    # Get time range
    timestamps = [m.get('timestamp') for m in messages if m.get('timestamp')]
    start_time = min(timestamps) if timestamps else None
    end_time = max(timestamps) if timestamps else None

    # Word count
    word_count = count_words(all_content)

    # Extract keywords
    keywords = extract_keywords(all_content)

    # Generate summary hint
    summary_hint = _generate_summary_hint(messages, classification, unique_paths)

    return ClassifiedExchange(
        exchange_id=str(uuid_module.uuid4()),
        classification=classification.value,
        importance=importance,
        messages=[m for m in messages],  # Keep original dicts
        summary_hint=summary_hint,
        file_paths=unique_paths[:10],  # Limit file paths
        start_time=start_time,
        end_time=end_time,
        word_count=word_count,
        keywords=keywords
    )


def _generate_summary_hint(
    messages: List[dict],
    classification: Classification,
    file_paths: List[str]
) -> str:
    """Generate a brief hint to help the summarizer."""
    hints = []

    # Classification-based hints
    hint_map = {
        Classification.DECISION: "Discuss the decision made and reasoning",
        Classification.FILE_CHANGE: "Describe what files were changed and why",
        Classification.ERROR_FIX: "Explain the error encountered and how it was fixed",
        Classification.DISCUSSION: "Summarize the technical discussion",
        Classification.IMPLEMENTATION: "Describe what was implemented",
        Classification.RESEARCH: "Summarize what was learned",
        Classification.CONFIGURATION: "Describe the configuration changes",
    }
    hints.append(hint_map.get(classification, "Summarize the key points"))

    # Add file context if present
    if file_paths:
        path_str = ", ".join(Path(p).name for p in file_paths[:3])
        hints.append(f"Files involved: {path_str}")

    return ". ".join(hints)


def classify_session(
    parsed_session: dict,
    min_length: int = 50,
    min_messages: int = 2
) -> List[ClassifiedExchange]:
    """
    Classify a complete parsed session.

    Args:
        parsed_session: Output from conversation-parser.py
        min_length: Minimum message length to consider
        min_messages: Minimum messages per exchange

    Returns:
        List of ClassifiedExchange objects
    """
    messages = parsed_session.get('messages', [])

    # Filter out skip-worthy messages
    filtered = [m for m in messages if not should_skip(m, min_length)]

    if not filtered:
        return []

    # Group into exchanges
    exchange_groups = group_into_exchanges(filtered, min_messages=min_messages)

    # Classify each exchange
    classified = []
    for group in exchange_groups:
        exchange = classify_exchange(group)
        # Final filter: skip low-value exchanges
        if exchange.classification != Classification.SKIP.value:
            classified.append(exchange)

    return classified


def main():
    parser = argparse.ArgumentParser(
        description="Classify conversation segments for indexing"
    )
    parser.add_argument("-f", "--file", type=Path,
                        help="JSONL session file to classify")
    parser.add_argument("--parsed-json", action="store_true",
                        help="Read pre-parsed JSON from stdin")
    parser.add_argument("--min-length", type=int, default=50,
                        help="Minimum message length (default: 50)")
    parser.add_argument("--min-messages", type=int, default=2,
                        help="Minimum messages per exchange (default: 2)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON (default)")
    parser.add_argument("--stats", action="store_true",
                        help="Output statistics only")

    args = parser.parse_args()

    # Get parsed session data
    if args.file:
        # Parse the file first
        from importlib.util import spec_from_file_location, module_from_spec
        parser_path = os.path.join(SCRIPT_DIR, "conversation-parser.py")
        spec = spec_from_file_location("conv_parser", parser_path)
        conv_parser = module_from_spec(spec)
        spec.loader.exec_module(conv_parser)

        session = conv_parser.parse_session_file(args.file)
        if not session:
            print(json.dumps({"error": f"Could not parse {args.file}"}))
            sys.exit(1)
        parsed_session = asdict(session)

    elif args.parsed_json or not sys.stdin.isatty():
        # Read pre-parsed JSON from stdin
        input_text = sys.stdin.read().strip()
        try:
            parsed_session = json.loads(input_text)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}))
            sys.exit(1)
    else:
        parser.error("Either --file or piped JSON input is required")

    # Classify
    exchanges = classify_session(
        parsed_session,
        min_length=args.min_length,
        min_messages=args.min_messages
    )

    # Output
    if args.stats:
        stats = {
            "session_id": parsed_session.get("session_id"),
            "total_exchanges": len(exchanges),
            "by_classification": {},
            "by_importance": {},
            "total_words": 0,
            "file_paths_found": 0
        }
        for ex in exchanges:
            cls = ex.classification
            imp = ex.importance
            stats["by_classification"][cls] = stats["by_classification"].get(cls, 0) + 1
            stats["by_importance"][imp] = stats["by_importance"].get(imp, 0) + 1
            stats["total_words"] += ex.word_count
            stats["file_paths_found"] += len(ex.file_paths)

        print(json.dumps(stats, indent=2))
    else:
        output = [asdict(ex) for ex in exchanges]
        print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
