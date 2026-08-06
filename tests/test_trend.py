"""django-query-guard: Unit tests for trend tracking and comparison engine.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest
from django_query_guard.trend import (
    TrendSnapshot,
    TrendComparison,
    save_trend_snapshot,
    compare_with_previous,
)


# ==============================================================================
# SECTION 1: TREND SNAPSHOT RECORDING TESTS
# ==============================================================================

def test_trend_snapshot_records_test_metrics():
    """Verify TrendSnapshot correctly captures test query metrics."""
    snapshot = TrendSnapshot()

    snapshot.record_test("test_api_list", query_count=3, max_queries=5, n_plus_one_detected=False, status="passed")
    snapshot.record_test("test_api_detail", query_count=30, max_queries=5, n_plus_one_detected=True, status="failed")

    data = snapshot.to_dict()

    assert data["summary"]["total_tests"] == 2
    assert data["summary"]["passed"] == 1
    assert data["summary"]["failed"] == 1
    assert data["summary"]["total_queries"] == 33
    assert data["summary"]["n_plus_one_count"] == 1
    assert len(data["tests"]) == 2


# ==============================================================================
# SECTION 2: TREND PERSISTENCE & LOADING TESTS
# ==============================================================================

def test_save_and_load_trend_history():
    """Verify trend snapshots persist to JSON file and can be loaded back."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tmp:
        tmp_path = tmp.name

    try:
        snapshot = TrendSnapshot()
        snapshot.record_test("test_orders", query_count=5, max_queries=10, n_plus_one_detected=False, status="passed")

        saved_data = save_trend_snapshot(snapshot, filepath=tmp_path)

        with open(tmp_path, "r", encoding="utf-8") as f:
            history = json.load(f)

        assert len(history) == 1
        assert history[0]["summary"]["total_queries"] == 5
    finally:
        os.unlink(tmp_path)


# ==============================================================================
# SECTION 3: TREND COMPARISON ENGINE TESTS
# ==============================================================================

def test_trend_comparison_detects_regression():
    """Verify TrendComparison correctly identifies query count regressions."""
    previous = {
        "summary": {"total_tests": 1, "passed": 1, "failed": 0, "total_queries": 3, "n_plus_one_count": 0},
        "tests": [{"test_name": "test_api", "query_count": 3}],
    }
    current = {
        "summary": {"total_tests": 1, "passed": 0, "failed": 1, "total_queries": 30, "n_plus_one_count": 1},
        "tests": [{"test_name": "test_api", "query_count": 30}],
    }

    comparison = TrendComparison(current=current, previous=previous)

    assert comparison.is_regression is True
    assert comparison.query_delta == 27
    assert comparison.n_plus_one_delta == 1

    per_test = comparison.per_test_deltas()
    assert len(per_test) == 1
    assert per_test[0]["delta"] == 27
    assert per_test[0]["direction"] == "[REGRESSION]"


def test_trend_comparison_detects_improvement():
    """Verify TrendComparison correctly identifies query count improvements."""
    previous = {
        "summary": {"total_tests": 1, "passed": 1, "failed": 0, "total_queries": 30, "n_plus_one_count": 0},
        "tests": [{"test_name": "test_api", "query_count": 30}],
    }
    current = {
        "summary": {"total_tests": 1, "passed": 1, "failed": 0, "total_queries": 3, "n_plus_one_count": 0},
        "tests": [{"test_name": "test_api", "query_count": 3}],
    }

    comparison = TrendComparison(current=current, previous=previous)

    assert comparison.is_improvement is True
    assert comparison.query_delta == -27

    per_test = comparison.per_test_deltas()
    assert per_test[0]["direction"] == "[IMPROVEMENT]"


def test_trend_comparison_format_summary_output():
    """Verify TrendComparison produces human-readable terminal summary."""
    previous = {
        "summary": {"total_tests": 2, "passed": 2, "failed": 0, "total_queries": 6, "n_plus_one_count": 0},
        "tests": [],
    }
    current = {
        "summary": {"total_tests": 2, "passed": 1, "failed": 1, "total_queries": 36, "n_plus_one_count": 1},
        "tests": [],
    }

    comparison = TrendComparison(current=current, previous=previous)
    summary = comparison.format_summary()

    assert "QUERY GUARD TREND COMPARISON" in summary
    assert "+30" in summary
    assert "+1" in summary
