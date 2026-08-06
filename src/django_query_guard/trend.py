"""django-query-guard: Query count trend tracker for historical comparison.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""
from __future__ import annotations

import datetime
import json
import os
from typing import Any


# ==============================================================================
# SECTION 1: TREND DATA SCHEMA & STORAGE
# ==============================================================================

DEFAULT_TREND_FILE = ".query_guard_history.json"


def _load_history(filepath: str) -> list[dict[str, Any]]:
    """Load existing trend history from JSON file."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_history(filepath: str, history: list[dict[str, Any]]) -> None:
    """Persist trend history to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, default=str)


# ==============================================================================
# SECTION 2: TREND SNAPSHOT RECORDER
# ==============================================================================

class TrendSnapshot:
    """Captures a single Pytest run's query metrics as a trend data point."""

    def __init__(self):
        self.test_metrics: list[dict[str, Any]] = []

    def record_test(
        self,
        test_name: str,
        query_count: int,
        max_queries: int | None,
        n_plus_one_detected: bool,
        status: str,
    ) -> None:
        """Record one test's query metrics for trend comparison."""
        self.test_metrics.append({
            "test_name": test_name,
            "query_count": query_count,
            "max_queries": max_queries,
            "n_plus_one_detected": n_plus_one_detected,
            "status": status,
        })

    def to_dict(self) -> dict[str, Any]:
        """Serialize snapshot to a dictionary for JSON storage."""
        total_queries = sum(m["query_count"] for m in self.test_metrics)
        total_tests = len(self.test_metrics)
        passed = sum(1 for m in self.test_metrics if m["status"] == "passed")
        failed = total_tests - passed
        n_plus_ones = sum(1 for m in self.test_metrics if m["n_plus_one_detected"])

        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "total_queries": total_queries,
                "n_plus_one_count": n_plus_ones,
            },
            "tests": self.test_metrics,
        }


# ==============================================================================
# SECTION 3: TREND COMPARISON ENGINE
# ==============================================================================

class TrendComparison:
    """Compares current run metrics against the previous run for regression detection."""

    def __init__(self, current: dict[str, Any], previous: dict[str, Any] | None):
        self.current = current
        self.previous = previous

    @property
    def has_previous(self) -> bool:
        return self.previous is not None

    @property
    def query_delta(self) -> int:
        """Change in total queries (positive = regression, negative = improvement)."""
        if not self.has_previous:
            return 0
        return (
            self.current["summary"]["total_queries"]
            - self.previous["summary"]["total_queries"]
        )

    @property
    def n_plus_one_delta(self) -> int:
        """Change in N+1 detections."""
        if not self.has_previous:
            return 0
        return (
            self.current["summary"]["n_plus_one_count"]
            - self.previous["summary"]["n_plus_one_count"]
        )

    @property
    def is_regression(self) -> bool:
        """True if query count increased or new N+1 patterns appeared."""
        return self.query_delta > 0 or self.n_plus_one_delta > 0

    @property
    def is_improvement(self) -> bool:
        """True if query count decreased."""
        return self.query_delta < 0

    def per_test_deltas(self) -> list[dict[str, Any]]:
        """Compare query counts per test between current and previous runs."""
        if not self.has_previous:
            return []

        prev_map = {t["test_name"]: t["query_count"] for t in self.previous.get("tests", [])}
        deltas = []

        for test in self.current.get("tests", []):
            name = test["test_name"]
            curr_count = test["query_count"]
            prev_count = prev_map.get(name)

            if prev_count is not None:
                delta = curr_count - prev_count
                if delta != 0:
                    deltas.append({
                        "test_name": name,
                        "previous": prev_count,
                        "current": curr_count,
                        "delta": delta,
                        "direction": "[REGRESSION]" if delta > 0 else "[IMPROVEMENT]",
                    })

        return deltas

    def format_summary(self) -> str:
        """Generate human-readable trend comparison summary for terminal output."""
        lines = [
            "",
            "=" * 72,
            " QUERY GUARD TREND COMPARISON ".center(72, "="),
            "=" * 72,
        ]

        curr_summary = self.current["summary"]
        lines.append(f"  Current Run:  {curr_summary['total_queries']} queries across {curr_summary['total_tests']} tests")

        if self.has_previous:
            prev_summary = self.previous["summary"]
            lines.append(f"  Previous Run: {prev_summary['total_queries']} queries across {prev_summary['total_tests']} tests")
            lines.append("")

            delta_symbol = "[REGRESSION]" if self.query_delta > 0 else "[IMPROVEMENT]" if self.query_delta < 0 else "[NO CHANGE]"
            delta_sign = f"+{self.query_delta}" if self.query_delta > 0 else str(self.query_delta)
            lines.append(f"  {delta_symbol} Query Delta: {delta_sign} queries")

            if self.n_plus_one_delta != 0:
                n1_sign = f"+{self.n_plus_one_delta}" if self.n_plus_one_delta > 0 else str(self.n_plus_one_delta)
                lines.append(f"  [WARNING] N+1 Delta: {n1_sign} patterns")

            per_test = self.per_test_deltas()
            if per_test:
                lines.append("")
                lines.append("  Per-Test Changes:")
                for td in per_test:
                    sign = f"+{td['delta']}" if td['delta'] > 0 else str(td['delta'])
                    lines.append(f"    {td['direction']} {td['test_name']}: {td['previous']} -> {td['current']} ({sign})")
        else:
            lines.append("  (No previous run data available for comparison)")

        lines.append("=" * 72)
        return "\n".join(lines)


# ==============================================================================
# SECTION 4: PUBLIC API FUNCTIONS
# ==============================================================================

def save_trend_snapshot(snapshot: TrendSnapshot, filepath: str = DEFAULT_TREND_FILE) -> dict[str, Any]:
    """Save current run snapshot to trend history file and return it."""
    history = _load_history(filepath)
    data = snapshot.to_dict()
    history.append(data)
    _save_history(filepath, history)
    return data


def compare_with_previous(
    current_data: dict[str, Any],
    filepath: str = DEFAULT_TREND_FILE,
) -> TrendComparison:
    """Load previous run from history and compare against current run."""
    history = _load_history(filepath)

    # Find the second-to-last entry (previous run)
    previous = None
    if len(history) >= 2:
        previous = history[-2]

    return TrendComparison(current=current_data, previous=previous)
