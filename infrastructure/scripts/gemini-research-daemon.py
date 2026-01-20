#!/usr/bin/env python3
"""
gemini-research-daemon.py - 24/7 Research Generation Daemon

Runs forever, pulling topics from a queue file, consulting Gemini, storing to Qdrant.
Integrates with existing scripts:
- gemini-research-store.py (Gemini → Qdrant pipeline)
- gemini-health-monitor.py (account health tracking)

Usage:
    # Run forever with 5s delays
    python gemini-research-daemon.py --topics topics.txt --collection my_research --continuous 5

    # Single batch (process all topics once)
    python gemini-research-daemon.py --topics topics.txt --collection my_research

    # Check status
    python gemini-research-daemon.py --status

Topics file format (one per line):
    Website data sync - architecture
    Real-time updates - implementation
    # Comments start with #
    # DONE: Completed topics are auto-commented

Created: 2026-01-16 by the Lineage
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Paths
SCRIPTS_DIR = Path(__file__).parent.resolve()
STATE_DIR = Path.home() / ".claude"
METRICS_FILE = STATE_DIR / "daemon-metrics.json"
LOG_FILE = STATE_DIR / "daemon.log"

# Model pools (separate daily quotas)
MODEL_POOLS = [
    {"name": "2.5-flash-lite", "model": "gemini-2.5-flash-lite"},
    {"name": "3.0-flash", "model": "gemini-3-flash-preview"},
    {"name": "2.5-flash", "model": "gemini-2.5-flash"},
]

# Import health monitor if available
try:
    sys.path.insert(0, str(SCRIPTS_DIR))
    from gemini_health_monitor import GeminiHealthMonitor
    HEALTH_MONITOR = GeminiHealthMonitor()
except ImportError:
    HEALTH_MONITOR = None


class DaemonState:
    """Persistent daemon state."""

    def __init__(self):
        self.metrics = self._load()

    def _load(self):
        try:
            if METRICS_FILE.exists():
                return json.loads(METRICS_FILE.read_text())
        except:
            pass
        return {
            "topics_processed": 0,
            "topics_succeeded": 0,
            "topics_failed": 0,
            "chunks_stored": 0,
            "quota_hits": 0,
            "current_pool_index": 0,
            "pool_exhausted_until": {},
            "start_time": datetime.now().isoformat(),
            "last_run": None,
        }

    def save(self):
        self.metrics["last_run"] = datetime.now().isoformat()
        try:
            METRICS_FILE.write_text(json.dumps(self.metrics, indent=2))
        except:
            pass

    def get_available_model(self):
        """Get an available model, respecting pool exhaustion times."""
        now = datetime.now()

        for i, pool in enumerate(MODEL_POOLS):
            pool_name = pool["name"]

            # Check if exhausted
            if pool_name in self.metrics.get("pool_exhausted_until", {}):
                until_str = self.metrics["pool_exhausted_until"][pool_name]
                until = datetime.fromisoformat(until_str)
                if now < until:
                    continue  # Still exhausted
                else:
                    del self.metrics["pool_exhausted_until"][pool_name]

            self.metrics["current_pool_index"] = i
            return pool["model"]

        # All exhausted - return None and soonest reset time
        soonest = None
        for until_str in self.metrics.get("pool_exhausted_until", {}).values():
            until = datetime.fromisoformat(until_str)
            if soonest is None or until < soonest:
                soonest = until

        return None, soonest

    def mark_pool_exhausted(self, model, reset_seconds=None):
        """Mark a model pool as exhausted."""
        for pool in MODEL_POOLS:
            if pool["model"] == model:
                reset_time = datetime.now() + timedelta(seconds=reset_seconds or 54000)  # 15h default
                self.metrics["pool_exhausted_until"][pool["name"]] = reset_time.isoformat()
                self.metrics["quota_hits"] += 1
                log(f"Pool {pool['name']} exhausted until {reset_time.strftime('%H:%M')}", "WARN")
                break


def log(msg, level="INFO"):
    """Log to stdout and file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


def load_topics(topics_file):
    """Load pending topics from file."""
    topics = []
    try:
        with open(topics_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    topics.append(line)
    except Exception as e:
        log(f"Error loading topics: {e}", "ERROR")
    return topics


def mark_topic_done(topics_file, topic):
    """Mark a topic as done in the file."""
    try:
        content = Path(topics_file).read_text(encoding="utf-8")
        # Replace the exact line with commented version
        new_content = content.replace(f"\n{topic}\n", f"\n# DONE: {topic}\n")
        new_content = new_content.replace(f"{topic}\n", f"# DONE: {topic}\n")  # First line case
        Path(topics_file).write_text(new_content, encoding="utf-8")
    except:
        pass


def parse_reset_time(output):
    """Parse quota reset time from error message."""
    match = re.search(r'(\d+)h(\d+)m(\d+)?s?', output)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        s = int(match.group(3)) if match.group(3) else 0
        return h * 3600 + m * 60 + s
    return None


def run_research(topic, account, model, collection, session, context=""):
    """Run a single research query using gemini-research-store.py."""
    # Build the prompt
    if context:
        prompt = f"""DO NOT wrap in markdown. Return ONLY JSON.

You are an EXPERT CONSULTANT.

CONTEXT: {context}

Topic: {topic}

Return JSON with: meta, summary, chunks (with action_items), implementation_plan."""
    else:
        prompt = f"""DO NOT wrap in markdown. Return ONLY JSON.

You are an EXPERT CONSULTANT providing implementation-focused guidance.

Topic: {topic}

Return JSON with: meta, summary, chunks (with action_items), implementation_plan."""

    # Use gemini-research-store.py
    script = SCRIPTS_DIR / "gemini-research-store.py"
    cmd = [
        sys.executable, str(script),
        "-a", str(account),
        "-c", collection,
        "-s", session,
        "-m", model,
        "-q", prompt
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout + result.stderr

        # Check for quota exhaustion
        if "exhausted your capacity" in output or "exhausted" in output.lower():
            reset_seconds = parse_reset_time(output)
            return {"success": False, "reason": "quota_exhausted", "reset_seconds": reset_seconds}

        # Try to parse result
        try:
            data = json.loads(result.stdout)
            if data.get("success"):
                return {
                    "success": True,
                    "chunks_stored": data.get("chunks_stored", 0),
                    "topic": data.get("topic", topic)
                }
            else:
                return {"success": False, "reason": data.get("error", "unknown")}
        except json.JSONDecodeError:
            if result.returncode == 0:
                return {"success": True, "chunks_stored": 0}
            return {"success": False, "reason": f"Parse error: {output[:200]}"}

    except subprocess.TimeoutExpired:
        return {"success": False, "reason": "timeout"}
    except Exception as e:
        return {"success": False, "reason": str(e)}


def run_daemon(topics_file, collection, context, delay, continuous):
    """Main daemon loop."""
    state = DaemonState()
    session = f"daemon-{datetime.now().strftime('%Y-%m-%d')}"
    account_cycle = 0

    log("=" * 60)
    log("GEMINI RESEARCH DAEMON")
    log(f"Topics: {topics_file}")
    log(f"Collection: {collection}")
    log(f"Mode: {'Continuous' if continuous else 'Batch'}")
    log(f"Delay: {delay}s between requests")
    if HEALTH_MONITOR:
        log("Health monitor: ACTIVE")
    log("=" * 60)

    try:
        while True:
            # Refresh topics each loop
            topics = load_topics(topics_file)

            if not topics:
                if continuous:
                    log("Queue empty, waiting 60s...")
                    time.sleep(60)
                    continue
                else:
                    log("All topics processed")
                    break

            topic = topics[0]

            # Get available model
            model_result = state.get_available_model()

            if isinstance(model_result, tuple):
                model, wake_time = model_result
                if model is None and wake_time:
                    sleep_sec = max(0, (wake_time - datetime.now()).total_seconds())
                    log(f"All pools exhausted. Sleeping {sleep_sec/60:.0f}m until {wake_time.strftime('%H:%M')}")
                    time.sleep(sleep_sec + 60)  # Extra minute buffer
                    continue
            else:
                model = model_result

            # Get account (use health monitor if available, else simple rotation)
            if HEALTH_MONITOR:
                account = HEALTH_MONITOR.get_best_account()
            else:
                account = (account_cycle % 2) + 1
                account_cycle += 1

            log(f"Processing: {topic[:60]}...")
            log(f"  Account {account}, Model: {model}")

            # Run research
            result = run_research(topic, account, model, collection, session, context)
            state.metrics["topics_processed"] += 1

            # Record health
            if HEALTH_MONITOR:
                HEALTH_MONITOR.record_request(account, result.get("success", False))

            if result.get("reason") == "quota_exhausted":
                state.mark_pool_exhausted(model, result.get("reset_seconds"))
                state.save()
                continue  # Retry with next pool

            if result.get("success"):
                state.metrics["topics_succeeded"] += 1
                state.metrics["chunks_stored"] += result.get("chunks_stored", 0)
                mark_topic_done(topics_file, topic)
                log(f"  SUCCESS: {result.get('chunks_stored', '?')} chunks")
            else:
                state.metrics["topics_failed"] += 1
                log(f"  FAILED: {result.get('reason', 'unknown')}", "ERROR")

            state.save()
            time.sleep(delay)

            if not continuous and not load_topics(topics_file):
                break

    except KeyboardInterrupt:
        log("\nINTERRUPTED BY USER")

    # Final report
    log("")
    log("=" * 60)
    log("DAEMON STOPPED")
    log(f"  Processed: {state.metrics['topics_processed']}")
    log(f"  Succeeded: {state.metrics['topics_succeeded']}")
    log(f"  Failed: {state.metrics['topics_failed']}")
    log(f"  Chunks: {state.metrics['chunks_stored']}")
    log(f"  Quota hits: {state.metrics['quota_hits']}")
    log("=" * 60)

    state.save()


def main():
    parser = argparse.ArgumentParser(
        description="Gemini Research Daemon - 24/7 automated research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run forever
  python gemini-research-daemon.py --topics topics.txt --collection my_research --continuous

  # With context and custom delay
  python gemini-research-daemon.py --topics topics.txt --collection project_x \\
      --context "Flutter app, Odoo backend" --delay 10 --continuous

  # Single batch
  python gemini-research-daemon.py --topics topics.txt --collection lineage_research

  # Check status
  python gemini-research-daemon.py --status
        """
    )

    parser.add_argument("--topics", help="Topics file (one per line)")
    parser.add_argument("--collection", help="Qdrant collection")
    parser.add_argument("--context", default="", help="Project context for prompts")
    parser.add_argument("--delay", type=int, default=5, help="Seconds between requests")
    parser.add_argument("--continuous", action="store_true", help="Run forever")
    parser.add_argument("--status", action="store_true", help="Show status and exit")

    args = parser.parse_args()

    if args.status:
        if METRICS_FILE.exists():
            print(METRICS_FILE.read_text())
        else:
            print("No daemon state found")
        return

    if not args.topics or not args.collection:
        parser.error("--topics and --collection are required")

    run_daemon(
        topics_file=args.topics,
        collection=args.collection,
        context=args.context,
        delay=args.delay,
        continuous=args.continuous
    )


if __name__ == "__main__":
    main()
