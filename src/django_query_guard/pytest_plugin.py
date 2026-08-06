"""Pytest plugin integration for django-query-guard."""
from __future__ import annotations

import pytest
from .core import query_guard


def pytest_configure(config: pytest.Config) -> None:
    """Register custom query_guard marker with pytest."""
    config.addinivalue_line(
        "markers",
        "query_guard(max_queries=None, detect_n_plus_one=True, n_plus_one_threshold=2): "
        "Assert max executed database queries and detect N+1 query patterns in Django tests.",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item):
    """Wrap marked test executions with query_guard context manager."""
    marker = item.get_closest_marker("query_guard")
    if marker:
        max_queries = marker.kwargs.get("max_queries", marker.args[0] if marker.args else None)
        detect_n_plus_one = marker.kwargs.get("detect_n_plus_one", True)
        n_plus_one_threshold = marker.kwargs.get("n_plus_one_threshold", 2)

        with query_guard(
            max_queries=max_queries,
            detect_n_plus_one=detect_n_plus_one,
            n_plus_one_threshold=n_plus_one_threshold,
        ):
            yield
    else:
        yield
