"""django-query-guard: N+1 Query Optimization Solution for GridViewFieldOptions.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""

from __future__ import annotations

from typing import Any, List, Dict, Set

# ==============================================================================
# SECTION 1: UNOPTIMIZED LEGACY IMPLEMENTATION (O(N) N+1 QUERY BLOAT)
# ==============================================================================

class LegacyGridViewHandler:
    """Simulates the buggy legacy implementation causing O(N) database queries."""

    def __init__(self, db_connection: Any):
        self.db = db_connection

    def create_missing_field_options(self, view_id: int, missing_field_ids: List[int]) -> int:
        """Legacy approach: Queries database inside list comprehension loop per missing field."""
        created_count = 0

        # ❌ N+1 BUG: For each missing field, re-queries field options twice from DB
        for field_id in missing_field_ids:
            # Simulated DB Query 1
            existing_options = self.db.query_existing_field_options(view_id)
            # Simulated DB Query 2
            hidden_fields = self.db.query_hidden_fields(view_id)

            if field_id not in existing_options:
                self.db.insert_field_option(view_id, field_id, hidden_fields)
                created_count += 1

        return created_count


# ==============================================================================
# SECTION 2: OPTIMIZED O(1) IMPLEMENTATION (ZERO N+1 DATABASE QUERIES)
# ==============================================================================

class OptimizedGridViewHandler:
    """Optimized implementation: Pre-fetches options once into memory before bulk creation."""

    def __init__(self, db_connection: Any):
        self.db = db_connection

    def create_missing_field_options(self, view_id: int, missing_field_ids: List[int]) -> int:
        """Optimized O(1) approach: Executes exactly 2 baseline queries regardless of N fields."""
        if not missing_field_ids:
            return 0

        # ✅ STEP 1: Pre-fetch existing options once into an in-memory set (1 Query)
        existing_options_set: Set[int] = set(self.db.query_existing_field_options(view_id))

        # ✅ STEP 2: Pre-fetch hidden fields once into memory (1 Query)
        hidden_fields: List[str] = self.db.query_hidden_fields(view_id)

        # ✅ STEP 3: Filter missing options entirely in-memory (0 Queries)
        new_field_options = [
            {"view_id": view_id, "field_id": fid, "hidden": hidden_fields}
            for fid in missing_field_ids
            if fid not in existing_options_set
        ]

        # ✅ STEP 4: Execute a single O(1) bulk insert operation (1 Query)
        if new_field_options:
            self.db.bulk_insert_field_options(new_field_options)

        return len(new_field_options)


# ==============================================================================
# SECTION 3: MOCK DATABASE CONNECTION FOR PERFORMANCE BENCHMARKING
# ==============================================================================

class MockDatabaseConnection:
    """Tracks executed query counts during benchmarking."""

    def __init__(self):
        self.query_count = 0
        self.existing_field_ids = {1, 2, 3}
        self.inserted_records = []

    def query_existing_field_options(self, view_id: int) -> List[int]:
        self.query_count += 1
        return list(self.existing_field_ids)

    def query_hidden_fields(self, view_id: int) -> List[str]:
        self.query_count += 1
        return ["hidden_meta_col"]

    def insert_field_option(self, view_id: int, field_id: int, hidden_fields: List[str]) -> None:
        self.query_count += 1
        self.inserted_records.append((view_id, field_id))

    def bulk_insert_field_options(self, records: List[Dict[str, Any]]) -> None:
        self.query_count += 1
        self.inserted_records.extend(records)
