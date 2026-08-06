"""Core context manager and query interceptor for django-query-guard."""
from __future__ import annotations

import time
from typing import Any, Callable
from django.db import connection

from .detector import NPlusOneDetector
from .exceptions import NPlusOneQueryError, QueryCountExceededError


class query_guard:
    """Context manager to monitor and restrict Django database query execution.

    Usage:
        with query_guard(max_queries=3, detect_n_plus_one=True):
            user = User.objects.get(id=1)
            profiles = list(user.profile_set.all())
    """

    def __init__(
        self,
        max_queries: int | None = None,
        detect_n_plus_one: bool = True,
        n_plus_one_threshold: int = 2,
    ):
        self.max_queries = max_queries
        self.detect_n_plus_one = detect_n_plus_one
        self.n_plus_one_threshold = n_plus_one_threshold
        self.captured_queries: list[dict[str, Any]] = []

    def _execute_wrapper(
        self,
        execute: Callable[..., Any],
        sql: str,
        params: tuple[Any, ...],
        many: bool,
        context: dict[str, Any],
    ) -> Any:
        start_time = time.time()
        try:
            return execute(sql, params, many, context)
        finally:
            duration = time.time() - start_time
            self.captured_queries.append({
                "sql": sql,
                "params": params,
                "duration": duration,
            })

    def __enter__(self) -> query_guard:
        self.captured_queries.clear()
        self._wrapper = connection.execute_wrapper(self._execute_wrapper)
        self._wrapper.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._wrapper.__exit__(exc_type, exc_val, exc_tb)

        # Do not raise query guard errors if an unhandled exception already occurred inside block
        if exc_type is not None:
            return

        query_count = len(self.captured_queries)

        # Check max queries limit
        if self.max_queries is not None and query_count > self.max_queries:
            raise QueryCountExceededError(
                executed_count=query_count,
                max_queries=self.max_queries,
                queries=self.captured_queries,
            )

        # Check N+1 query patterns
        if self.detect_n_plus_one:
            detector = NPlusOneDetector(threshold=self.n_plus_one_threshold)
            n_plus_ones = detector.analyze(self.captured_queries)
            if n_plus_ones:
                # Pick the most repeated N+1 pattern
                pattern, occurrences = max(n_plus_ones.items(), key=lambda item: len(item[1]))
                raise NPlusOneQueryError(
                    pattern=pattern,
                    count=len(occurrences),
                    occurrences=occurrences,
                )
