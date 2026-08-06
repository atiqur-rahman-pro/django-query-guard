"""django-query-guard: Unit tests for GridViewFieldOptions N+1 query optimization.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""

from __future__ import annotations

import pytest
from django_query_guard import query_guard, QueryCountExceededError
from examples.gridview_fix import (
    LegacyGridViewHandler,
    OptimizedGridViewHandler,
    MockDatabaseConnection,
)

# ==============================================================================
# SECTION 1: BENCHMARK UNOPTIMIZED LEGACY IMPLEMENTATION WITH DJANGO-QUERY-GUARD
# ==============================================================================

@pytest.mark.django_db
def test_legacy_handler_fails_django_query_guard_threshold():
    """Verify that legacy handler triggers QueryCountExceededError in django-query-guard."""
    db = MockDatabaseConnection()
    handler = LegacyGridViewHandler(db)

    missing_field_ids = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 10 fields

    # ❌ Legacy implementation executes 30 DB Queries, failing django-query-guard limit
    with pytest.raises(QueryCountExceededError) as exc_info:
        with query_guard(max_queries=5, detect_n_plus_one=False):
            handler.create_missing_field_options(view_id=100, missing_field_ids=missing_field_ids)

    assert exc_info.value.executed_count == 30
    assert exc_info.value.max_queries == 5


# ==============================================================================
# SECTION 2: VERIFY OPTIMIZED IMPLEMENTATION PASSES DJANGO-QUERY-GUARD
# ==============================================================================

@pytest.mark.django_db
def test_optimized_handler_passes_django_query_guard_budget():
    """Verify that optimized O(1) handler passes django-query-guard strict limit of 3 queries."""
    db = MockDatabaseConnection()
    handler = OptimizedGridViewHandler(db)

    missing_field_ids = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 10 fields

    # ✅ Optimized implementation executes exactly 3 DB Queries, passing django-query-guard budget
    with query_guard(max_queries=3, detect_n_plus_one=True):
        created = handler.create_missing_field_options(view_id=100, missing_field_ids=missing_field_ids)

    assert created == 10
    assert db.query_count == 3
