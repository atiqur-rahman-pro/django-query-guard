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
from examples.gridview_fix import (
    LegacyGridViewHandler,
    OptimizedGridViewHandler,
    MockDatabaseConnection,
)

# ==============================================================================
# SECTION 1: BENCHMARK UNOPTIMIZED LEGACY IMPLEMENTATION (O(N) QUERIES)
# ==============================================================================

def test_legacy_handler_triggers_n_plus_one_queries():
    """Verify that legacy handler scales O(N) database queries with N missing fields."""
    db = MockDatabaseConnection()
    handler = LegacyGridViewHandler(db)

    missing_field_ids = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 10 fields
    created = handler.create_missing_field_options(view_id=100, missing_field_ids=missing_field_ids)

    assert created == 10
    # ❌ Legacy executed (2 queries per field * 10) + 10 individual inserts = 30 DB Queries!
    assert db.query_count == 30


# ==============================================================================
# SECTION 2: VERIFY OPTIMIZED IMPLEMENTATION (O(1) CONSTANT QUERIES)
# ==============================================================================

def test_optimized_handler_executes_constant_o_1_queries():
    """Verify that optimized handler executes constant 3 queries regardless of N missing fields."""
    db = MockDatabaseConnection()
    handler = OptimizedGridViewHandler(db)

    missing_field_ids = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 10 fields
    created = handler.create_missing_field_options(view_id=100, missing_field_ids=missing_field_ids)

    assert created == 10
    # ✅ Optimized executed exactly 3 DB Queries (1 pre-fetch options + 1 hidden fields + 1 bulk insert)
    assert db.query_count == 3
