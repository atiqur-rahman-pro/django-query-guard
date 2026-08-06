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
from .report import QueryGuardReportData, HTMLReportGenerator, write_html_report
from .trend import TrendSnapshot, TrendComparison, save_trend_snapshot, compare_with_previous

__version__ = "0.2.0"
__author__ = "Atiqur Rahman <rahman.atiqur.pro@gmail.com>"
__all__ = [
    "query_guard",
    "NPlusOneDetector",
    "normalize_sql",
    "QueryGuardError",
    "QueryCountExceededError",
    "NPlusOneQueryError",
    "QueryGuardReportData",
    "HTMLReportGenerator",
    "write_html_report",
    "TrendSnapshot",
    "TrendComparison",
    "save_trend_snapshot",
    "compare_with_previous",
]
