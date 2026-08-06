"""Custom exceptions for django-query-guard."""

class QueryGuardError(Exception):
    """Base exception for django-query-guard."""
    pass


class QueryCountExceededError(QueryGuardError):
    """Raised when total executed database queries exceed the allowed max limit."""
    def __init__(self, executed_count: int, max_queries: int, queries: list[dict]):
        self.executed_count = executed_count
        self.max_queries = max_queries
        self.queries = queries
        message = (
            f"Query limit exceeded: executed {executed_count} queries, "
            f"max allowed is {max_queries}."
        )
        super().__init__(message)


class NPlusOneQueryError(QueryGuardError):
    """Raised when N+1 query patterns or duplicate queries are detected."""
    def __init__(self, pattern: str, count: int, occurrences: list[dict]):
        self.pattern = pattern
        self.count = count
        self.occurrences = occurrences
        message = (
            f"N+1 Query pattern detected! Normalized query executed {count} times:\n"
            f"  {pattern}"
        )
        super().__init__(message)
