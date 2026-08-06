"""django-query-guard: Custom exceptions and formatted error reporters.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""
from __future__ import annotations

from typing import Any


def format_section(title: str, fill_char: str = "=", width: int = 72) -> str:
    """Format a centered section header line with divider characters."""
    return f" {title} ".center(width, fill_char)


class QueryGuardError(Exception):
    """Base exception for django-query-guard."""
    pass


class QueryCountExceededError(QueryGuardError):
    """Raised when total executed database queries exceed the allowed max limit."""

    def __init__(self, executed_count: int, max_queries: int, queries: list[dict[str, Any]]):
        self.executed_count = executed_count
        self.max_queries = max_queries
        self.queries = queries

        lines = [
            "",
            format_section("QUERY GUARD LIMIT EXCEEDED", "="),
            f"Executed {executed_count} queries, max allowed limit is {max_queries}.",
            format_section("EXECUTED SQL QUERIES", "-"),
        ]

        for idx, q in enumerate(queries, 1):
            sql = q.get("sql", "").strip()
            duration = q.get("duration", 0.0)
            lines.append(f"  {idx}. {sql} ({duration:.4f}s)")

        lines.append(format_section("END QUERY GUARD REPORT", "="))
        message = "\n".join(lines)
        super().__init__(message)


class NPlusOneQueryError(QueryGuardError):
    """Raised when N+1 query patterns or duplicate queries are detected."""

    def __init__(self, pattern: str, count: int, occurrences: list[dict[str, Any]]):
        self.pattern = pattern
        self.count = count
        self.occurrences = occurrences

        lines = [
            "",
            format_section("N+1 QUERY PATTERN DETECTED", "="),
            f"Normalized query executed {count} times in a single operation:",
            f"  👉 {pattern}",
            format_section("EXECUTED OCCURRENCES", "-"),
        ]

        for idx, q in enumerate(occurrences, 1):
            sql = q.get("sql", "").strip()
            duration = q.get("duration", 0.0)
            lines.append(f"  {idx}. {sql} ({duration:.4f}s)")

        lines.append(format_section("END QUERY GUARD REPORT", "="))
        message = "\n".join(lines)
        super().__init__(message)
