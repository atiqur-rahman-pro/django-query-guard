"""django-query-guard: Detect and prevent N+1 queries in Django applications."""

from .core import query_guard
from .detector import NPlusOneDetector, normalize_sql
from .exceptions import NPlusOneQueryError, QueryCountExceededError, QueryGuardError

__version__ = "0.1.0"
__all__ = [
    "query_guard",
    "NPlusOneDetector",
    "normalize_sql",
    "QueryGuardError",
    "QueryCountExceededError",
    "NPlusOneQueryError",
]
