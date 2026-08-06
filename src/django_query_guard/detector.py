"""django-query-guard: SQL normalization and N+1 query pattern analyzer.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


def normalize_sql(sql: str) -> str:
    """Normalize a raw SQL string by replacing variable parameters/literals with placeholders.

    Replaces:
    - Numeric literals (e.g. `WHERE id = 42` -> `WHERE id = ?`)
    - Quoted string literals (e.g. `WHERE name = 'alice'` -> `WHERE name = ?`)
    - IN clause lists (e.g. `WHERE id IN (1, 2, 3)` -> `WHERE id IN (?)`)
    - Whitespace normalization
    """
    if not sql:
        return ""

    normalized = sql.strip()

    # Replace string literals '...' or "..."
    normalized = re.sub(r"'(?:''|[^'])*'", "?", normalized)
    normalized = re.sub(r'"(?:""|[^"])*"', "?", normalized)

    # Replace IN (...) lists with IN (?)
    normalized = re.sub(r"\bIN\s*\([^)]+\)", "IN (?)", normalized, flags=re.IGNORECASE)

    # Replace integer and float numbers (not inside identifiers)
    normalized = re.sub(r"\b\d+\.?\d*\b", "?", normalized)

    # Collapse multiple whitespace characters into a single space
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized


class NPlusOneDetector:
    """Analyzes a list of captured Django query dictionaries for N+1 query patterns."""

    def __init__(self, threshold: int = 2):
        """
        :param threshold: Minimum number of duplicate normalized queries to consider as N+1 pattern.
        """
        self.threshold = threshold

    def analyze(self, queries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Analyze captured query list and group queries by normalized SQL string.

        Returns a dictionary mapping normalized_sql -> list of query records for patterns
        that occur >= self.threshold times.
        """
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for q in queries:
            sql = q.get("sql", "")
            if not sql:
                continue
            norm = normalize_sql(sql)
            grouped[norm].append(q)

        # Filter patterns that exceed or meet repetition threshold
        n_plus_ones = {
            norm: occurrences
            for norm, occurrences in grouped.items()
            if len(occurrences) >= self.threshold
        }

        return n_plus_ones
