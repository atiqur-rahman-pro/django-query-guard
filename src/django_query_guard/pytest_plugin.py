"""django-query-guard: Pytest plugin integration with HTML report & trend tracking.

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
import time

import pytest
from .core import query_guard
from .exceptions import QueryCountExceededError, NPlusOneQueryError
from .report import QueryGuardReportData, write_html_report
from .trend import TrendSnapshot, save_trend_snapshot, compare_with_previous


# ==============================================================================
# SECTION 1: PYTEST CLI OPTIONS REGISTRATION
# ==============================================================================

def pytest_addoption(parser: pytest.Parser) -> None:
    """Register django-query-guard CLI options for HTML reports and trend tracking."""
    group = parser.getgroup("query-guard", "django-query-guard options")

    group.addoption(
        "--query-guard-report",
        action="store",
        default=None,
        metavar="PATH",
        help="Generate HTML query guard report at specified path (e.g. --query-guard-report=report.html)",
    )

    group.addoption(
        "--query-guard-trend",
        action="store",
        default=None,
        metavar="PATH",
        help="Enable trend tracking with JSON history file (e.g. --query-guard-trend=.query_guard_history.json)",
    )


# ==============================================================================
# SECTION 2: MARKER REGISTRATION & SESSION SETUP
# ==============================================================================

def pytest_configure(config: pytest.Config) -> None:
    """Register custom query_guard marker and initialize report/trend collectors."""
    config.addinivalue_line(
        "markers",
        "query_guard(max_queries=None, detect_n_plus_one=True, n_plus_one_threshold=2): "
        "Assert max executed database queries and detect N+1 query patterns in Django tests.",
    )

    # Initialize shared report data collector
    config._query_guard_report_data = QueryGuardReportData()
    config._query_guard_trend_snapshot = TrendSnapshot()


# ==============================================================================
# SECTION 3: TEST EXECUTION HOOK WITH QUERY GUARD WRAPPER
# ==============================================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item):
    """Wrap marked test executions with query_guard context manager and collect metrics."""
    marker = item.get_closest_marker("query_guard")
    if marker:
        max_queries = marker.kwargs.get("max_queries", marker.args[0] if marker.args else None)
        detect_n_plus_one = marker.kwargs.get("detect_n_plus_one", True)
        n_plus_one_threshold = marker.kwargs.get("n_plus_one_threshold", 2)

        guard = query_guard(
            max_queries=max_queries,
            detect_n_plus_one=detect_n_plus_one,
            n_plus_one_threshold=n_plus_one_threshold,
        )

        start_time = time.time()
        status = "passed"
        error_msg = ""
        n_plus_one_detected = False

        try:
            with guard:
                yield
        except (QueryCountExceededError, NPlusOneQueryError) as exc:
            status = "failed"
            error_msg = str(exc)
            n_plus_one_detected = isinstance(exc, NPlusOneQueryError)
            raise
        except Exception:
            status = "failed"
            raise
        else:
            status = "passed"
        finally:
            duration = time.time() - start_time
            query_count = len(guard.captured_queries)

            # Collect data for HTML report
            report_data: QueryGuardReportData = item.config._query_guard_report_data
            report_data.add_test_result(
                test_name=item.nodeid,
                status=status,
                query_count=query_count,
                max_queries=max_queries,
                n_plus_one_detected=n_plus_one_detected,
                queries=guard.captured_queries.copy(),
                duration=duration,
                error_message=error_msg,
            )

            # Collect data for trend tracking
            trend_snapshot: TrendSnapshot = item.config._query_guard_trend_snapshot
            trend_snapshot.record_test(
                test_name=item.nodeid,
                query_count=query_count,
                max_queries=max_queries,
                n_plus_one_detected=n_plus_one_detected,
                status=status,
            )
    else:
        yield


# ==============================================================================
# SECTION 4: SESSION FINISH — HTML REPORT GENERATION & TREND COMPARISON
# ==============================================================================

def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Generate HTML report and run trend comparison at the end of the Pytest session."""
    report_data: QueryGuardReportData = session.config._query_guard_report_data
    trend_snapshot: TrendSnapshot = session.config._query_guard_trend_snapshot

    # --- HTML Report Generation ---
    report_path = session.config.getoption("--query-guard-report", default=None)
    if report_path and report_data.total_tests > 0:
        abs_path = os.path.abspath(report_path)
        write_html_report(report_data, abs_path)
        print(f"\n[django-query-guard] HTML report generated: {abs_path}")

    # --- Trend Tracking & Comparison ---
    trend_path = session.config.getoption("--query-guard-trend", default=None)
    if trend_path and trend_snapshot.test_metrics:
        current_data = save_trend_snapshot(trend_snapshot, filepath=trend_path)
        comparison = compare_with_previous(current_data, filepath=trend_path)
        print(comparison.format_summary())
