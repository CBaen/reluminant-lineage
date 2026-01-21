#!/usr/bin/env python3
"""
extract-chunk.py - Run 3 Gemini passes + Opus confirmation on a single chunk

Uses gemini-api-call.py (Python SDK) for reliable Windows execution.

Usage:
    python extract-chunk.py --chunk-file chunk.txt --episode 2 --chunk-index 5
    python extract-chunk.py --chunk-text "The letter was rediscovered..." --episode 2 --chunk-index 1
    echo "chunk text" | python extract-chunk.py --episode 2 --chunk-index 1

Output: JSON array of validated extractions ready for Qdrant storage
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Paths
SCRIPTS_DIR = Path.home() / ".claude" / "scripts"
GEMINI_API_CALL = SCRIPTS_DIR / "gemini-api-call.py"

# Content types to extract
CONTENT_TYPES = [
    "historical_fact",
    "lore_fact",
    "character_state",
    "open_mystery",
    "proposed_question",
    "used_imagery",
    "used_sensory_language",
    "relationship"
]

# Extraction prompts for each pass
PROMPT_TEMPLATE = """Extract structured narrative data from this documentary script chunk.

CHUNK (Episode {episode}, Chunk {chunk_index}):
\"\"\"
{chunk_text}
\"\"\"

CONTEXT: This is from "Tesla Mandela Effects" - a documentary series blending real history with invented lore. Characters like George Bliss may APPEAR historical but are unverifiable.

Extract as JSON array with these content types:
1. historical_fact - ONLY things independently verifiable (Carrington Event = yes, George Bliss = no)
2. lore_fact - Series-invented canon (fiction presented as fact)
3. character_state - Subjective experience/belief of a character
4. open_mystery - Questions deliberately left unanswered
5. used_sensory_language - Distinctive metaphors worth tracking

For EACH extraction include:
- content_type
- text (the extracted content)
- reasoning (WHY you classified it this way)
- confidence (0.0-1.0)

{instruction}

Return ONLY a valid JSON array. No markdown, no explanation.
"""

INSTRUCTIONS = {
    "precise": "Be PRECISE - only extract what is explicitly stated. Conservative classification.",
    "moderate": "Look for both obvious and subtle elements. Balanced classification.",
    "exploratory": "Be EXPLORATORY - find thematic implications and nuanced meanings."
}


def call_gemini(prompt: str, account: int) -> tuple[bool, str]:
    """
    Call Gemini via PowerShell + CLI (already authenticated via OAuth).

    Account parameter is noted for future use but CLI uses single auth currently.
    """
    try:
        # Write prompt to temp file to avoid shell escaping issues
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(prompt)
            prompt_file = f.name

        try:
            # Use gemini CLI via PowerShell (already OAuth authenticated)
            model = "gemini-2.5-flash"  # Good balance of quality and speed

            # Read from file to avoid escaping issues
            ps_command = f'Get-Content -Path "{prompt_file}" -Raw | gemini -m {model} --output-format text'

            result = subprocess.run(
                ["powershell.exe", "-NonInteractive", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=150,
                env={**os.environ}
            )

            if result.returncode == 0 and result.stdout.strip():
                # Remove credential message if present
                output = result.stdout.replace("Loaded cached credentials.", "").strip()
                return True, output
            else:
                return False, result.stderr or "Empty response"
        finally:
            # Clean up temp file
            os.unlink(prompt_file)

    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)


def extract_json(text: str) -> list:
    """Extract JSON array from potentially contaminated output."""
    # Remove common contamination
    text = text.replace("Loaded cached credentials.", "").strip()

    # Remove markdown code blocks if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    # Try to find JSON array
    start = text.find("[")
    end = text.rfind("]") + 1

    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    # Try the whole thing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []


def run_gemini_pass(chunk_text: str, episode: int, chunk_index: int,
                    instruction_key: str, account: int) -> list:
    """Run one Gemini extraction pass."""
    prompt = PROMPT_TEMPLATE.format(
        episode=episode,
        chunk_index=chunk_index,
        chunk_text=chunk_text,
        instruction=INSTRUCTIONS[instruction_key]
    )

    success, response = call_gemini(prompt, account)

    if success:
        extractions = extract_json(response)
        # Tag each extraction with the pass
        for item in extractions:
            item["_pass"] = instruction_key
        return extractions
    else:
        print(f"[WARN] Pass {instruction_key} failed: {response}", file=sys.stderr)
        return []


def similarity_key(item: dict) -> str:
    """Create a key for matching similar extractions across passes."""
    # Use content type + first 50 chars of text
    text = item.get("text", "")[:50].lower()
    ctype = item.get("content_type", "")
    return f"{ctype}:{text}"


def vote_on_extractions(pass1: list, pass2: list, pass3: list) -> tuple[list, list]:
    """
    Compare extractions from 3 passes and vote.

    Returns:
        (agreed_items, disagreed_items)
    """
    # Group by similarity
    all_items = {}

    for item in pass1 + pass2 + pass3:
        key = similarity_key(item)
        if key not in all_items:
            all_items[key] = {"items": [], "passes": set()}
        all_items[key]["items"].append(item)
        all_items[key]["passes"].add(item.get("_pass", "unknown"))

    agreed = []
    disagreed = []

    for key, data in all_items.items():
        agreement = len(data["passes"])

        # Take the item with highest confidence
        best_item = max(data["items"], key=lambda x: x.get("confidence", 0))

        if agreement >= 2:
            # 2/3 or 3/3 agreement - accept
            best_item["_agreement"] = f"{agreement}/3"
            best_item["_final_confidence"] = 0.95 if agreement == 3 else 0.85

            # Remove internal fields before output
            clean_item = {k: v for k, v in best_item.items() if not k.startswith("_")}
            clean_item["confidence"] = best_item["_final_confidence"]
            clean_item["agreement"] = best_item["_agreement"]

            agreed.append(clean_item)
        else:
            # No agreement - needs Opus
            best_item["_needs_opus"] = True
            disagreed.append(best_item)

    return agreed, disagreed


def main():
    parser = argparse.ArgumentParser(description="Extract semantic data from episode chunk")
    parser.add_argument("--chunk-file", "-f", help="File containing chunk text")
    parser.add_argument("--chunk-text", "-t", help="Chunk text directly")
    parser.add_argument("--episode", "-e", type=int, required=True, help="Episode number")
    parser.add_argument("--chunk-index", "-c", type=int, required=True, help="Chunk index")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--skip-opus", action="store_true", help="Skip Opus confirmation")

    args = parser.parse_args()

    # Get chunk text
    if args.chunk_file:
        with open(args.chunk_file, 'r', encoding='utf-8') as f:
            chunk_text = f.read()
    elif args.chunk_text:
        chunk_text = args.chunk_text
    else:
        chunk_text = sys.stdin.read()

    if not chunk_text.strip():
        print("ERROR: No chunk text provided", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Starting 3-pass extraction for Episode {args.episode}, Chunk {args.chunk_index}", file=sys.stderr)

    # Pass 1: Precise (Account 1)
    print("[INFO] Pass 1/3: Precise extraction (Account 1)...", file=sys.stderr)
    pass1 = run_gemini_pass(chunk_text, args.episode, args.chunk_index, "precise", 1)
    print(f"[INFO] Pass 1 found {len(pass1)} items", file=sys.stderr)

    time.sleep(5)  # Rate limiting

    # Pass 2: Moderate (Account 2)
    print("[INFO] Pass 2/3: Moderate extraction (Account 2)...", file=sys.stderr)
    pass2 = run_gemini_pass(chunk_text, args.episode, args.chunk_index, "moderate", 2)
    print(f"[INFO] Pass 2 found {len(pass2)} items", file=sys.stderr)

    time.sleep(5)  # Rate limiting

    # Pass 3: Exploratory (Account 1)
    print("[INFO] Pass 3/3: Exploratory extraction (Account 1)...", file=sys.stderr)
    pass3 = run_gemini_pass(chunk_text, args.episode, args.chunk_index, "exploratory", 1)
    print(f"[INFO] Pass 3 found {len(pass3)} items", file=sys.stderr)

    # Vote
    print("[INFO] Comparing extractions...", file=sys.stderr)
    agreed, disagreed = vote_on_extractions(pass1, pass2, pass3)

    print(f"[INFO] Agreement: {len(agreed)} items accepted, {len(disagreed)} need Opus", file=sys.stderr)

    # Add episode/chunk metadata
    for item in agreed:
        item["episode_number"] = args.episode
        item["chunk_index"] = args.chunk_index

    # Output
    result = {
        "episode": args.episode,
        "chunk_index": args.chunk_index,
        "extractions": agreed,
        "needs_opus_review": len(disagreed),
        "disagreed_items": []  # Separate file for Opus review
    }

    # Save disagreed items for Opus review (separate file)
    if disagreed and not args.skip_opus:
        review_file = args.output.replace('.json', '-needs-review.json') if args.output else None
        if review_file:
            review_data = {
                "episode": args.episode,
                "chunk_index": args.chunk_index,
                "context": "Items where Gemini passes disagreed. Review and classify.",
                "items": []
            }
            for item in disagreed:
                review_item = {
                    "text": item.get("text"),
                    "gemini_classification": item.get("content_type"),
                    "gemini_reasoning": item.get("reasoning"),
                    "gemini_confidence": item.get("confidence"),
                    "found_by_pass": item.get("_pass"),
                    "your_classification": None,  # To be filled by Opus
                    "your_reasoning": None
                }
                review_data["items"].append(review_item)

            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump(review_data, f, indent=2)
            print(f"[INFO] Review file written to {review_file}", file=sys.stderr)
            result["review_file"] = review_file

    output_json = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"[INFO] Output written to {args.output}", file=sys.stderr)
    else:
        print(output_json)

    print(f"[DONE] Extraction complete", file=sys.stderr)


if __name__ == "__main__":
    main()
