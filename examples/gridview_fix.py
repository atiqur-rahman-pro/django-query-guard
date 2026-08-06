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
from django.db import connection
from django_query_guard import query_guard

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
# SECTION 2: OPTIMIZED O(1) IMPLEMENTATION WITH DJANGO-QUERY-GUARD
# ==============================================================================

class OptimizedGridViewHandler:
    """Optimized implementation: Pre-fetches options once into memory before bulk creation."""

    def __init__(self, db_connection: Any):
        self.db = db_connection

    def create_missing_field_options(self, view_id: int, missing_field_ids: List[int]) -> int:
        """Optimized O(1) approach protected by django-query-guard max_queries limit."""
        if not missing_field_ids:
            return 0

        # Protect execution with django-query-guard budget of max 3 queries
        with query_guard(max_queries=3, detect_n_plus_one=True):
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
# SECTION 3: DJANGO DATABASE CONNECTION FOR REAL ORM QUERY INTERACTION
# ==============================================================================

class MockDatabaseConnection:
    """Executes real SQLite cursor queries intercepted by django-query-guard."""

    def __init__(self):
        self.query_count = 0
        self.existing_field_ids = {1, 2, 3}
        self.inserted_records = []

    def query_existing_field_options(self, view_id: int) -> List[int]:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM auth_user WHERE id IN (1, 2, 3)")
        self.query_count += 1
        return list(self.existing_field_ids)

    def query_hidden_fields(self, view_id: int) -> List[str]:
        with connection.cursor() as cursor:
            cursor.execute("SELECT username FROM auth_user LIMIT 1")
        self.query_count += 1
        return ["hidden_meta_col"]

    def insert_field_option(self, view_id: int, field_id: int, hidden_fields: List[str]) -> None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        self.query_count += 1
        self.inserted_records.append((view_id, field_id))

    def bulk_insert_field_options(self, records: List[Dict[str, Any]]) -> None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        self.query_count += 1
        self.inserted_records.extend(records)
