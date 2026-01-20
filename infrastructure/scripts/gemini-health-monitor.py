#!/usr/bin/env python3
"""
gemini-health-monitor.py - Health monitoring for Gemini workers

Tracks rate limits, implements circuit breakers, handles account rotation.

Usage:
    from gemini_health_monitor import GeminiHealthMonitor

    monitor = GeminiHealthMonitor()
    account = monitor.get_best_account()
    success = monitor.record_request(account, success=True)

Or as CLI:
    python gemini-health-monitor.py status
    python gemini-health-monitor.py reset
"""

import argparse
import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# State file location
STATE_FILE = Path(os.path.expanduser("~/.claude/gemini-health-state.json"))

# Configuration
RPM_LIMIT = 60
RPM_WARN_THRESHOLD = 50  # 83% of limit
CIRCUIT_BREAK_THRESHOLD = 3  # Failures before opening
CIRCUIT_OPEN_TIMEOUT = 60  # Seconds to wait before half-open


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class AccountHealth:
    """Health tracking for a single Gemini account."""
    account_id: int
    request_timestamps: list = field(default_factory=list)
    consecutive_failures: int = 0
    total_requests: int = 0
    total_successes: int = 0
    circuit_state: str = "closed"
    circuit_opened_at: Optional[float] = None
    last_request_at: Optional[float] = None

    @property
    def rpm(self) -> int:
        """Current requests per minute."""
        now = time.time()
        cutoff = now - 60
        # Clean old timestamps
        self.request_timestamps = [t for t in self.request_timestamps if t > cutoff]
        return len(self.request_timestamps)

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.total_successes / self.total_requests) * 100

    @property
    def is_available(self) -> bool:
        """Check if account is available for requests."""
        if self.circuit_state == CircuitState.OPEN.value:
            # Check if timeout has passed
            if self.circuit_opened_at:
                if time.time() - self.circuit_opened_at > CIRCUIT_OPEN_TIMEOUT:
                    self.circuit_state = CircuitState.HALF_OPEN.value
                    return True
            return False
        return True

    def record_request(self, success: bool) -> None:
        """Record a request result."""
        now = time.time()
        self.request_timestamps.append(now)
        self.last_request_at = now
        self.total_requests += 1

        if success:
            self.total_successes += 1
            self.consecutive_failures = 0
            if self.circuit_state == CircuitState.HALF_OPEN.value:
                # Recovery - close circuit
                self.circuit_state = CircuitState.CLOSED.value
                self.circuit_opened_at = None
        else:
            self.consecutive_failures += 1
            if self.consecutive_failures >= CIRCUIT_BREAK_THRESHOLD:
                # Open circuit breaker
                self.circuit_state = CircuitState.OPEN.value
                self.circuit_opened_at = now

    def reset(self) -> None:
        """Reset health tracking."""
        self.request_timestamps = []
        self.consecutive_failures = 0
        self.total_requests = 0
        self.total_successes = 0
        self.circuit_state = CircuitState.CLOSED.value
        self.circuit_opened_at = None
        self.last_request_at = None


class GeminiHealthMonitor:
    """Health monitor for Gemini accounts."""

    def __init__(self):
        self.accounts = {
            1: AccountHealth(account_id=1),
            2: AccountHealth(account_id=2)
        }
        self._load_state()

    def _load_state(self) -> None:
        """Load state from file."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    for account_id, state in data.get("accounts", {}).items():
                        aid = int(account_id)
                        if aid in self.accounts:
                            for key, value in state.items():
                                if hasattr(self.accounts[aid], key):
                                    setattr(self.accounts[aid], key, value)
            except Exception:
                pass  # Start fresh on error

    def _save_state(self) -> None:
        """Save state to file."""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "accounts": {
                str(aid): asdict(acc) for aid, acc in self.accounts.items()
            },
            "updated_at": datetime.now().isoformat()
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def get_best_account(self) -> int:
        """Get the best available account based on health metrics."""
        available = []

        for aid, acc in self.accounts.items():
            if acc.is_available:
                # Score based on: lower RPM is better, higher success rate is better
                rpm_score = (RPM_LIMIT - acc.rpm) / RPM_LIMIT
                success_score = acc.success_rate / 100
                score = rpm_score * 0.6 + success_score * 0.4
                available.append((aid, score))

        if not available:
            # All circuits open - return account 1 and hope
            return 1

        # Return account with highest score
        available.sort(key=lambda x: x[1], reverse=True)
        return available[0][0]

    def record_request(self, account_id: int, success: bool) -> dict:
        """Record a request result and return health status."""
        if account_id not in self.accounts:
            return {"error": f"Unknown account: {account_id}"}

        acc = self.accounts[account_id]
        acc.record_request(success)
        self._save_state()

        # Check for warnings
        warnings = []
        if acc.rpm >= RPM_WARN_THRESHOLD:
            warnings.append(f"Account {account_id} approaching rate limit: {acc.rpm}/{RPM_LIMIT} RPM")

        if acc.circuit_state == CircuitState.OPEN.value:
            warnings.append(f"Account {account_id} circuit breaker OPEN")

        return {
            "account_id": account_id,
            "rpm": acc.rpm,
            "circuit_state": acc.circuit_state,
            "success_rate": f"{acc.success_rate:.1f}%",
            "warnings": warnings
        }

    def get_status(self) -> dict:
        """Get current health status of all accounts."""
        status = {
            "accounts": {},
            "recommended_account": self.get_best_account(),
            "timestamp": datetime.now().isoformat()
        }

        for aid, acc in self.accounts.items():
            status["accounts"][aid] = {
                "rpm": acc.rpm,
                "circuit_state": acc.circuit_state,
                "success_rate": f"{acc.success_rate:.1f}%",
                "consecutive_failures": acc.consecutive_failures,
                "total_requests": acc.total_requests,
                "available": acc.is_available
            }

        return status

    def reset(self, account_id: Optional[int] = None) -> None:
        """Reset health tracking for one or all accounts."""
        if account_id:
            if account_id in self.accounts:
                self.accounts[account_id].reset()
        else:
            for acc in self.accounts.values():
                acc.reset()
        self._save_state()


def main():
    parser = argparse.ArgumentParser(description="Gemini Health Monitor CLI")
    parser.add_argument("command", choices=["status", "reset", "best"],
                       help="Command: status, reset, or best")
    parser.add_argument("--account", type=int, help="Account ID (1 or 2)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    monitor = GeminiHealthMonitor()

    if args.command == "status":
        status = monitor.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("Gemini Health Status")
            print("=" * 50)
            for aid, acc_status in status["accounts"].items():
                state_icon = "[OK]" if acc_status["circuit_state"] == "closed" else "[OPEN]"
                print(f"\nAccount {aid}: {state_icon}")
                print(f"  RPM: {acc_status['rpm']}/{RPM_LIMIT}")
                print(f"  Success Rate: {acc_status['success_rate']}")
                print(f"  Circuit: {acc_status['circuit_state']}")
                print(f"  Available: {acc_status['available']}")
            print(f"\nRecommended: Account {status['recommended_account']}")

    elif args.command == "reset":
        monitor.reset(args.account)
        print(f"Reset {'account ' + str(args.account) if args.account else 'all accounts'}")

    elif args.command == "best":
        best = monitor.get_best_account()
        if args.json:
            print(json.dumps({"best_account": best}))
        else:
            print(best)


if __name__ == "__main__":
    main()
