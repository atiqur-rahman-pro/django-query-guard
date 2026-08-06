"""django-query-guard: Unit tests for HTML report generation.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""
from __future__ import annotations

import os
import tempfile

import pytest
from django_query_guard.report import QueryGuardReportData, HTMLReportGenerator, write_html_report


# ==============================================================================
# SECTION 1: REPORT DATA COLLECTOR TESTS
# ==============================================================================

def test_report_data_collector_tracks_passed_and_failed_tests():
    """Verify QueryGuardReportData correctly aggregates pass/fail counts."""
    data = QueryGuardReportData()

    data.add_test_result(
        test_name="test_api_list",
        status="passed",
        query_count=2,
        max_queries=5,
        n_plus_one_detected=False,
        queries=[],
        duration=0.01,
    )
    data.add_test_result(
        test_name="test_api_detail",
        status="failed",
        query_count=30,
        max_queries=5,
        n_plus_one_detected=True,
        queries=[{"sql": "SELECT * FROM users WHERE id = 1", "duration": 0.001}],
        duration=0.05,
    )

    assert data.total_tests == 2
    assert data.passed_tests == 1
    assert data.failed_tests == 1
    assert data.total_queries == 32
    assert data.n_plus_one_count == 1


# ==============================================================================
# SECTION 2: HTML REPORT GENERATOR TESTS
# ==============================================================================

def test_html_report_generator_produces_valid_html():
    """Verify HTMLReportGenerator outputs well-formed HTML with key elements."""
    data = QueryGuardReportData()
    data.add_test_result(
        test_name="test_users_api",
        status="passed",
        query_count=3,
        max_queries=5,
        n_plus_one_detected=False,
        queries=[],
        duration=0.02,
    )

    generator = HTMLReportGenerator(data)
    html_output = generator.generate()

    assert "<!DOCTYPE html>" in html_output
    assert "django-query-guard Report" in html_output
    assert "test_users_api" in html_output
    assert "PASS" in html_output
    assert "Atiqur Rahman" in html_output


# ==============================================================================
# SECTION 3: HTML FILE WRITE TESTS
# ==============================================================================

def test_write_html_report_creates_file_on_disk():
    """Verify write_html_report produces a valid HTML file."""
    data = QueryGuardReportData()
    data.add_test_result(
        test_name="test_products_list",
        status="failed",
        query_count=100,
        max_queries=5,
        n_plus_one_detected=True,
        queries=[
            {"sql": "SELECT * FROM products WHERE category_id = 1", "duration": 0.002},
            {"sql": "SELECT * FROM products WHERE category_id = 2", "duration": 0.003},
        ],
        duration=0.1,
    )

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        result_path = write_html_report(data, tmp_path)
        assert os.path.exists(result_path)

        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "test_products_list" in content
        assert "FAIL" in content
        assert "SELECT * FROM products" in content
    finally:
        os.unlink(tmp_path)
