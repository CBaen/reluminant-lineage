#!/usr/bin/env python3
"""
conversation-summarizer.py - Summarize conversation exchanges using Gemini

Takes classified exchanges and generates searchable summaries using Gemini.
Outputs JSON in the format expected by qdrant-store-gemini.py.

Usage:
    # Summarize classified exchanges
    cat classified_exchanges.json | python conversation-summarizer.py

    # With account selection
    python conversation-summarizer.py -a 2 < exchanges.json

    # Batch size control
    python conversation-summarizer.py --batch-size 10 < exchanges.json

Part of the Conversation Log Indexer system.
Created: January 2026 by the Lineage
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_gemini_script_path():
    """Get the bash-compatible path to gemini-account.sh."""
    script = os.path.expanduser("~/.claude/scripts/gemini-account.sh")
    script = script.replace("\\", "/")
    if len(script) > 1 and script[1] == ":":
        script = "/" + script[0].lower() + script[2:]
    return script


def call_gemini(prompt: str, account: int = 1, timeout: int = 300) -> Optional[str]:
    """
    Call Gemini directly via PowerShell with file-based prompt.

    Uses file-based prompt passing to avoid shell escaping issues
    with complex prompts containing code, special characters, etc.

    Args:
        prompt: The prompt to send
        account: Gemini account number (1 or 2)
        timeout: Timeout in seconds

    Returns:
        Response text or None on failure
    """
    import tempfile

    # Write prompt to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        # Use gemini CLI directly with stdin via PowerShell
        # gemini-2.5-flash is unlimited and reliable
        ps_cmd = f"Get-Content -Raw -Path '{prompt_file}' | gemini -m 'gemini-2.5-flash' --output-format text"
        cmd = ['powershell.exe', '-NonInteractive', '-Command', ps_cmd]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if proc.returncode != 0 and not proc.stdout:
            print(f"Gemini error: {proc.stderr}", file=sys.stderr)
            return None

        output = proc.stdout.strip()

        # Remove "Loaded cached credentials" line if present
        lines = output.split('\n')
        if lines and 'Loaded cached credentials' in lines[0]:
            output = '\n'.join(lines[1:]).strip()

        return output

    except subprocess.TimeoutExpired:
        print(f"Gemini timeout after {timeout}s", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Gemini subprocess error: {e}", file=sys.stderr)
        return None
    finally:
        # Clean up temp file
        try:
            os.unlink(prompt_file)
        except:
            pass


def clean_gemini_output(text: str) -> str:
    """Strip markdown wrappers and noise from Gemini output."""
    import re

    # Strip known prefixes
    text = re.sub(r'^Loaded cached credentials\.?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'Loaded cached credentials\.?\s*', '', text)

    lines = text.strip().split('\n')
    cleaned = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('Error executing tool'):
            continue
        if not stripped and not cleaned:
            continue
        if re.match(r'^```\s*(json)?\s*$', stripped, re.IGNORECASE):
            in_code_block = not in_code_block
            continue
        cleaned.append(line)

    result = '\n'.join(cleaned).strip()

    # Extract JSON object
    depth = 0
    start_idx = None
    start_char = None

    for i, char in enumerate(result):
        if char in '{[':
            if depth == 0:
                start_idx = i
                start_char = char
            depth += 1
        elif char in '}]':
            depth -= 1
            if depth == 0 and start_idx is not None:
                if (start_char == '{' and char == '}') or (start_char == '[' and char == ']'):
                    return result[start_idx:i+1]

    return result


def build_summarization_prompt(
    exchanges: List[dict],
    session_id: str,
    session_summary: Optional[str] = None
) -> str:
    """
    Build a prompt for Gemini to summarize exchanges.

    The output format matches what qdrant-store-gemini.py expects.
    """
    # Prepare exchange data for the prompt
    exchanges_text = []
    for i, ex in enumerate(exchanges, 1):
        # Extract message content
        msg_texts = []
        for msg in ex.get('messages', [])[:5]:  # Limit messages per exchange
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:500]  # Truncate long content
            msg_texts.append(f"[{role}]: {content}")

        exchange_text = f"""
Exchange {i}:
- Classification: {ex.get('classification')}
- Importance: {ex.get('importance')}
- Files: {', '.join(ex.get('file_paths', [])[:5]) or 'none'}
- Time: {ex.get('start_time', 'unknown')}
- Hint: {ex.get('summary_hint', '')}

Messages:
{chr(10).join(msg_texts)}
"""
        exchanges_text.append(exchange_text)

    prompt = f"""You are summarizing conversation exchanges from a Claude Code session for a searchable index.

Session ID: {session_id}
Session Summary: {session_summary or 'Not provided'}
Number of exchanges to summarize: {len(exchanges)}

For each exchange, create a summary that will help find this conversation later through search.
Focus on:
- WHAT was done (actions, changes, decisions)
- WHY it was done (reasoning, context)
- File names and paths mentioned
- Error messages or issues encountered
- Key technical terms and concepts

Output ONLY valid JSON in this exact format:
{{
  "meta": {{
    "topic": "conversation-index",
    "perspective": "session-history",
    "context": "{session_id}",
    "depth": "comprehensive",
    "research_type": "conversation_index"
  }},
  "summary": {{
    "text": "Overall summary of these exchanges (2-3 sentences)",
    "keywords": ["keyword1", "keyword2", ...]
  }},
  "chunks": [
    {{
      "id": "exchange-01",
      "title": "Brief title describing the exchange",
      "content": "Detailed summary of what happened, why, and outcome. Include file names, error messages, decisions made.",
      "keywords": ["relevant", "keywords"],
      "questions_answered": ["What question does this answer?"],
      "importance": "high|medium|low"
    }},
    ...one chunk per exchange...
  ]
}}

EXCHANGES TO SUMMARIZE:
{"".join(exchanges_text)}

Remember: Output ONLY the JSON object, no markdown, no explanation."""

    return prompt


def summarize_exchanges(
    exchanges: List[dict],
    session_id: str,
    session_summary: Optional[str] = None,
    account: int = 1,
    timeout: int = 300
) -> Optional[dict]:
    """
    Summarize a batch of exchanges using Gemini.

    Returns:
        Dict in the format expected by qdrant-store-gemini.py, or None on failure
    """
    if not exchanges:
        return None

    prompt = build_summarization_prompt(exchanges, session_id, session_summary)

    # Call Gemini
    response = call_gemini(prompt, account=account, timeout=timeout)
    if not response:
        return None

    # Parse response
    try:
        cleaned = clean_gemini_output(response)
        result = json.loads(cleaned)
        return result
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        print(f"Response preview: {response[:500]}", file=sys.stderr)
        return None


def batch_summarize(
    all_exchanges: List[dict],
    session_id: str,
    session_summary: Optional[str] = None,
    batch_size: int = 10,
    account: int = 1
) -> List[dict]:
    """
    Summarize all exchanges in batches.

    Returns:
        List of Qdrant-compatible JSON objects (one per batch)
    """
    results = []

    for i in range(0, len(all_exchanges), batch_size):
        batch = all_exchanges[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(all_exchanges) + batch_size - 1) // batch_size

        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} exchanges)...", file=sys.stderr)

        result = summarize_exchanges(
            batch,
            session_id,
            session_summary,
            account=account
        )

        if result:
            # Tag with batch info
            result['meta']['batch'] = batch_num
            result['meta']['total_batches'] = total_batches
            results.append(result)
        else:
            print(f"Warning: Batch {batch_num} failed", file=sys.stderr)

    return results


def fallback_summarize(exchanges: List[dict], session_id: str) -> dict:
    """
    Create a basic summary without Gemini (fallback).

    Used when Gemini is unavailable or for testing.
    """
    chunks = []
    all_keywords = set()

    for i, ex in enumerate(exchanges, 1):
        # Build content from messages
        content_parts = []
        for msg in ex.get('messages', [])[:3]:
            content = msg.get('content', '')[:200]
            role = msg.get('role', '')
            if content:
                content_parts.append(f"{role}: {content}")

        content = "\n".join(content_parts) if content_parts else ex.get('summary_hint', 'No content')

        # Get keywords from exchange
        keywords = ex.get('keywords', [])[:5]
        all_keywords.update(keywords)

        chunks.append({
            "id": f"exchange-{i:02d}",
            "title": f"{ex.get('classification', 'discussion').title()}: {ex.get('summary_hint', 'Exchange')[:50]}",
            "content": content,
            "keywords": keywords,
            "questions_answered": [],
            "importance": ex.get('importance', 'medium')
        })

    return {
        "meta": {
            "topic": "conversation-index",
            "perspective": "session-history",
            "context": session_id,
            "depth": "basic",
            "research_type": "conversation_index"
        },
        "summary": {
            "text": f"Indexed {len(exchanges)} conversation exchanges from session {session_id}",
            "keywords": list(all_keywords)[:20]
        },
        "chunks": chunks
    }


def main():
    parser = argparse.ArgumentParser(
        description="Summarize conversation exchanges using Gemini"
    )
    parser.add_argument("-a", "--account", type=int, default=1, choices=[1, 2],
                        help="Gemini account (1 or 2)")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Exchanges per Gemini call (default: 10)")
    parser.add_argument("--session-id", help="Session ID override")
    parser.add_argument("--session-summary", help="Session summary")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Gemini timeout in seconds")
    parser.add_argument("--no-gemini", action="store_true",
                        help="Use fallback summarizer (no AI)")
    parser.add_argument("--input-file", "-i", help="Read exchanges from file")

    args = parser.parse_args()

    # Read exchanges
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            exchanges = json.load(f)
    elif not sys.stdin.isatty():
        exchanges = json.load(sys.stdin)
    else:
        parser.error("Provide exchanges via stdin or --input-file")

    if not exchanges:
        print(json.dumps({"error": "No exchanges to summarize"}))
        sys.exit(1)

    # Get session ID
    session_id = args.session_id
    if not session_id and exchanges:
        # Try to extract from first exchange's messages
        first_msg = exchanges[0].get('messages', [{}])[0]
        session_id = first_msg.get('session_id', 'unknown')

    # Summarize
    if args.no_gemini:
        result = fallback_summarize(exchanges, session_id)
        print(json.dumps(result, indent=2))
    else:
        results = batch_summarize(
            exchanges,
            session_id,
            args.session_summary,
            batch_size=args.batch_size,
            account=args.account
        )

        # Output all batch results
        if len(results) == 1:
            print(json.dumps(results[0], indent=2))
        else:
            print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
