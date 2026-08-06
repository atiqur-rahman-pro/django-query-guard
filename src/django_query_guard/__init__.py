"""django-query-guard: Detect and prevent N+1 queries in Django applications.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""

from .core import query_guard
from .detector import NPlusOneDetector, normalize_sql
from .exceptions import NPlusOneQueryError, QueryCountExceededError, QueryGuardError

__version__ = "0.1.1"
__author__ = "Atiqur Rahman <rahman.atiqur.pro@gmail.com>"
__all__ = [
    "query_guard",
    "NPlusOneDetector",
    "normalize_sql",
    "QueryGuardError",
    "QueryCountExceededError",
    "NPlusOneQueryError",
]
