#!/usr/bin/env python3
"""
gemini-api-call.py - Direct Gemini API calls with fallback and timeout

Uses the google-generativeai Python SDK instead of the agentic CLI.
This provides:
- Direct API access (no agentic actions)
- Proper timeout handling
- Account rotation and model fallback
- Clean JSON responses

Usage:
    python gemini-api-call.py --account 1 --prompt "Your prompt"
    python gemini-api-call.py --account 1 --prompt-file prompt.txt
    python gemini-api-call.py --account 1 --prompt "query" --model gemini-2.5-flash

Account credentials are loaded from ~/.gemini/oauth_creds_account{1,2}.json

Created: January 2026
Purpose: Replace agentic CLI with direct API for consultation workflows
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
except ImportError:
    print("ERROR: google-generativeai not installed. Run: pip install google-generativeai", file=sys.stderr)
    sys.exit(1)


# Model fallback chain - quality first
MODEL_CHAIN = [
    "gemini-2.5-pro-preview-05-06",      # Highest quality
    "gemini-2.0-pro-exp-02-05",          # Pro experimental
    "gemini-2.0-flash",                   # Good quality, fast
    "gemini-1.5-flash",                   # Reliable fallback
]

# Account credential paths
GEMINI_DIR = os.path.expanduser("~/.gemini")
FALLBACK_LOG = os.path.join(GEMINI_DIR, "fallback.log")

# Timeouts and retries
CALL_TIMEOUT = 90  # seconds
MAX_RETRIES = 2
RETRY_DELAY = 5  # seconds


def log_fallback(msg: str):
    """Log fallback events."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {msg}"
    print(f"[FALLBACK] {msg}", file=sys.stderr)
    try:
        with open(FALLBACK_LOG, 'a') as f:
            f.write(log_entry + "\n")
    except:
        pass


def load_api_key(account: int) -> str:
    """Load API key for the specified account."""
    # Try environment variable first
    env_var = f"GEMINI_API_KEY_{account}"
    if env_var in os.environ:
        return os.environ[env_var]

    # Try API key file
    key_file = os.path.join(GEMINI_DIR, f"api_key_account{account}.txt")
    if os.path.exists(key_file):
        with open(key_file, 'r') as f:
            return f.read().strip()

    # Fallback to generic key
    if "GEMINI_API_KEY" in os.environ:
        return os.environ["GEMINI_API_KEY"]

    generic_key_file = os.path.join(GEMINI_DIR, "api_key.txt")
    if os.path.exists(generic_key_file):
        with open(generic_key_file, 'r') as f:
            return f.read().strip()

    raise ValueError(f"No API key found for account {account}. "
                    f"Set {env_var} or create {key_file}")


def call_gemini(prompt: str, model: str, api_key: str, timeout: int = CALL_TIMEOUT) -> tuple[bool, str, str]:
    """
    Make a single Gemini API call.

    Returns:
        (success: bool, response: str, error: str)
    """
    try:
        genai.configure(api_key=api_key)

        generation_config = {
            "temperature": 0,  # Deterministic for structured output
            "max_output_tokens": 65536,  # Maximum allowed
        }

        model_obj = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config
        )

        # Make the API call with timeout
        # Note: The SDK doesn't have a direct timeout, but we can use request_options
        response = model_obj.generate_content(
            prompt,
            request_options={"timeout": timeout}
        )

        if response.text:
            return True, response.text, ""
        else:
            return False, "", "Empty response from Gemini"

    except google_exceptions.ResourceExhausted as e:
        error_str = str(e).lower()
        if "quota" in error_str or "daily" in error_str:
            return False, "", f"QUOTA_EXHAUSTED: {e}"
        else:
            return False, "", f"RATE_LIMITED: {e}"
    except google_exceptions.InvalidArgument as e:
        return False, "", f"INVALID_MODEL: {e}"
    except google_exceptions.DeadlineExceeded as e:
        return False, "", f"TIMEOUT: {e}"
    except Exception as e:
        return False, "", f"ERROR: {e}"


def call_with_fallback(prompt: str, start_account: int, start_model: str = None, timeout: int = CALL_TIMEOUT) -> tuple[bool, str]:
    """
    Call Gemini with automatic account rotation and model fallback.

    Returns:
        (success: bool, response_or_error: str)
    """
    models_to_try = MODEL_CHAIN.copy()

    # If a specific model was requested, start from there
    if start_model:
        try:
            idx = models_to_try.index(start_model)
            models_to_try = models_to_try[idx:]
        except ValueError:
            # Model not in chain, try it first anyway
            models_to_try.insert(0, start_model)

    accounts = [1, 2] if start_account == 1 else [2, 1]

    for model in models_to_try:
        for account in accounts:
            try:
                api_key = load_api_key(account)
            except ValueError as e:
                log_fallback(f"SKIP: Account {account} - {e}")
                continue

            for attempt in range(1, MAX_RETRIES + 1):
                success, response, error = call_gemini(prompt, model, api_key, timeout=timeout)

                if success:
                    if model != (start_model or MODEL_CHAIN[0]) or account != start_account:
                        log_fallback(f"SUCCESS: {start_model or MODEL_CHAIN[0]}/acct{start_account} -> {model}/acct{account}")
                    return True, response

                # Check error type
                if "QUOTA_EXHAUSTED" in error:
                    log_fallback(f"QUOTA: {model}/acct{account} exhausted")
                    break  # Try next account/model

                if "INVALID_MODEL" in error:
                    log_fallback(f"SKIP: {model} not available")
                    break  # Try next model

                if "RATE_LIMITED" in error or "TIMEOUT" in error:
                    if attempt < MAX_RETRIES:
                        print(f"[RETRY] {error} - waiting {RETRY_DELAY}s...", file=sys.stderr)
                        time.sleep(RETRY_DELAY)
                        continue
                    log_fallback(f"RATE: {model}/acct{account} rate limited after {MAX_RETRIES} retries")
                    break  # Try next account/model

                # Other error - log and continue
                log_fallback(f"ERROR: {model}/acct{account} - {error}")
                break

    log_fallback("FAILED: All models exhausted on all accounts")
    return False, "All Gemini models exhausted on all accounts"


def main():
    parser = argparse.ArgumentParser(
        description="Direct Gemini API calls with fallback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python gemini-api-call.py -a 1 -q "What is Python?"
    python gemini-api-call.py -a 1 --prompt-file prompt.txt
    python gemini-api-call.py -a 2 -q "query" -m gemini-2.0-flash

Model fallback chain (quality-first):
    gemini-2.5-pro-preview-05-06 → gemini-2.0-pro-exp-02-05 →
    gemini-2.0-flash → gemini-1.5-flash
        """
    )

    parser.add_argument("-a", "--account", type=int, choices=[1, 2], default=1,
                        help="Account to use (1 or 2)")
    parser.add_argument("-q", "--query", help="Query/prompt")
    parser.add_argument("--prompt-file", "-p", help="Read prompt from file")
    parser.add_argument("-m", "--model", help="Start with specific model")
    parser.add_argument("--timeout", type=int, default=CALL_TIMEOUT,
                        help=f"Timeout in seconds (default: {CALL_TIMEOUT})")
    parser.add_argument("--json", action="store_true",
                        help="Output result as JSON with metadata")

    args = parser.parse_args()

    # Get prompt
    if args.prompt_file:
        with open(os.path.expanduser(args.prompt_file), 'r', encoding='utf-8') as f:
            prompt = f.read()
    elif args.query:
        prompt = args.query
    else:
        # Read from stdin
        prompt = sys.stdin.read()

    if not prompt.strip():
        print("ERROR: No prompt provided", file=sys.stderr)
        sys.exit(1)

    # Make the call (timeout is passed through call_with_fallback to call_gemini)
    success, result = call_with_fallback(prompt, args.account, args.model, timeout=args.timeout)

    if args.json:
        output = {
            "success": success,
            "account": args.account,
            "model": args.model,
            "response" if success else "error": result
        }
        print(json.dumps(output, indent=2))
    else:
        print(result)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
