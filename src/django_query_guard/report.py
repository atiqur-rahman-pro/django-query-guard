"""django-query-guard: HTML report generator for query analysis results.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""
from __future__ import annotations

import datetime
import html
from typing import Any


# ==============================================================================
# SECTION 1: HTML TEMPLATE ENGINE
# ==============================================================================

REPORT_CSS = """
:root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-card: #1e293b;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --accent-green: #22c55e;
    --accent-red: #ef4444;
    --accent-amber: #f59e0b;
    --accent-blue: #3b82f6;
    --accent-purple: #a855f7;
    --border-color: #334155;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    padding: 2rem;
}
.container { max-width: 1200px; margin: 0 auto; }

/* Header */
.header {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 2rem;
}
.header h1 {
    font-size: 2rem;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.header .subtitle { color: var(--text-secondary); font-size: 0.95rem; }

/* Summary Cards */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}
.summary-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: transform 0.2s;
}
.summary-card:hover { transform: translateY(-2px); }
.summary-card .value {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}
.summary-card .label {
    color: var(--text-secondary);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.green { color: var(--accent-green); }
.red { color: var(--accent-red); }
.amber { color: var(--accent-amber); }
.blue { color: var(--accent-blue); }

/* Test Result Table */
.results-section { margin-bottom: 2rem; }
.results-section h2 {
    font-size: 1.3rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-color);
}
table {
    width: 100%;
    border-collapse: collapse;
    background: var(--bg-card);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border-color);
}
th {
    background: var(--bg-secondary);
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-secondary);
}
td {
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--border-color);
    font-size: 0.9rem;
}
tr:hover { background: rgba(59, 130, 246, 0.05); }

.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-pass { background: rgba(34, 197, 94, 0.15); color: var(--accent-green); }
.badge-fail { background: rgba(239, 68, 68, 0.15); color: var(--accent-red); }
.badge-warn { background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); }

/* SQL Details */
.sql-block {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    font-family: 'Fira Code', 'Consolas', monospace;
    font-size: 0.8rem;
    overflow-x: auto;
    color: var(--accent-blue);
}

/* Footer */
.footer {
    text-align: center;
    padding: 1.5rem 0;
    border-top: 1px solid var(--border-color);
    color: var(--text-secondary);
    font-size: 0.8rem;
}
.footer a { color: var(--accent-blue); text-decoration: none; }
"""


# ==============================================================================
# SECTION 2: REPORT DATA COLLECTOR
# ==============================================================================

class QueryGuardReportData:
    """Collects query guard test results during a Pytest session."""

    def __init__(self):
        self.test_results: list[dict[str, Any]] = []
        self.session_start: float = 0.0
        self.session_end: float = 0.0

    def add_test_result(
        self,
        test_name: str,
        status: str,
        query_count: int,
        max_queries: int | None,
        n_plus_one_detected: bool,
        queries: list[dict[str, Any]],
        duration: float,
        error_message: str = "",
    ) -> None:
        """Record a single test's query guard outcome."""
        self.test_results.append({
            "test_name": test_name,
            "status": status,
            "query_count": query_count,
            "max_queries": max_queries,
            "n_plus_one_detected": n_plus_one_detected,
            "queries": queries,
            "duration": duration,
            "error_message": error_message,
        })

    @property
    def total_tests(self) -> int:
        return len(self.test_results)

    @property
    def passed_tests(self) -> int:
        return sum(1 for r in self.test_results if r["status"] == "passed")

    @property
    def failed_tests(self) -> int:
        return sum(1 for r in self.test_results if r["status"] == "failed")

    @property
    def total_queries(self) -> int:
        return sum(r["query_count"] for r in self.test_results)

    @property
    def n_plus_one_count(self) -> int:
        return sum(1 for r in self.test_results if r["n_plus_one_detected"])


# ==============================================================================
# SECTION 3: HTML REPORT GENERATOR
# ==============================================================================

class HTMLReportGenerator:
    """Generates a premium dark-themed HTML report from collected query guard data."""

    def __init__(self, report_data: QueryGuardReportData):
        self.data = report_data

    def generate(self) -> str:
        """Generate complete HTML report string."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        test_rows = self._build_test_rows()
        sql_details = self._build_sql_details()

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>django-query-guard Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>{REPORT_CSS}</style>
</head>
<body>
<div class="container">

    <!-- Header -->
    <div class="header">
        <h1>🛡️ django-query-guard Report</h1>
        <p class="subtitle">Generated on {html.escape(now)} &mdash; Automated N+1 Query Detection & Performance Analysis</p>
    </div>

    <!-- Summary Cards -->
    <div class="summary-grid">
        <div class="summary-card">
            <div class="value blue">{self.data.total_tests}</div>
            <div class="label">Total Tests</div>
        </div>
        <div class="summary-card">
            <div class="value green">{self.data.passed_tests}</div>
            <div class="label">Passed</div>
        </div>
        <div class="summary-card">
            <div class="value red">{self.data.failed_tests}</div>
            <div class="label">Failed</div>
        </div>
        <div class="summary-card">
            <div class="value amber">{self.data.total_queries}</div>
            <div class="label">Total Queries</div>
        </div>
        <div class="summary-card">
            <div class="value red">{self.data.n_plus_one_count}</div>
            <div class="label">N+1 Detected</div>
        </div>
    </div>

    <!-- Test Results Table -->
    <div class="results-section">
        <h2>📋 Test Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Queries</th>
                    <th>Max Allowed</th>
                    <th>N+1</th>
                    <th>Duration</th>
                </tr>
            </thead>
            <tbody>
                {test_rows}
            </tbody>
        </table>
    </div>

    <!-- SQL Query Details -->
    <div class="results-section">
        <h2>🔍 SQL Query Details</h2>
        {sql_details}
    </div>

    <!-- Footer -->
    <div class="footer">
        <p>Powered by <a href="https://pypi.org/project/django-query-guard/">django-query-guard</a>
        &mdash; Created by <a href="https://github.com/atiqur-rahman-pro">Atiqur Rahman</a></p>
    </div>

</div>
</body>
</html>"""

    def _build_test_rows(self) -> str:
        """Build HTML table rows for each test result."""
        rows = []
        for result in self.data.test_results:
            status_badge = (
                '<span class="badge badge-pass">✅ PASS</span>'
                if result["status"] == "passed"
                else '<span class="badge badge-fail">❌ FAIL</span>'
            )
            n_plus_one_badge = (
                '<span class="badge badge-fail">⚠️ YES</span>'
                if result["n_plus_one_detected"]
                else '<span class="badge badge-pass">—</span>'
            )
            max_q = str(result["max_queries"]) if result["max_queries"] is not None else "∞"
            query_color = "red" if result["max_queries"] and result["query_count"] > result["max_queries"] else "green"

            rows.append(f"""
                <tr>
                    <td>{html.escape(result['test_name'])}</td>
                    <td>{status_badge}</td>
                    <td class="{query_color}">{result['query_count']}</td>
                    <td>{max_q}</td>
                    <td>{n_plus_one_badge}</td>
                    <td>{result['duration']:.4f}s</td>
                </tr>
            """)
        return "\n".join(rows)

    def _build_sql_details(self) -> str:
        """Build SQL query detail blocks for failed tests."""
        blocks = []
        for result in self.data.test_results:
            if result["status"] == "failed" and result["queries"]:
                queries_html = "\n".join(
                    f"{idx}. {html.escape(q.get('sql', '').strip())} ({q.get('duration', 0.0):.4f}s)"
                    for idx, q in enumerate(result["queries"], 1)
                )
                blocks.append(f"""
                    <h3 style="margin: 1rem 0 0.5rem; color: var(--accent-red);">
                        ❌ {html.escape(result['test_name'])}
                    </h3>
                    <div class="sql-block"><pre>{queries_html}</pre></div>
                """)

        if not blocks:
            return '<p style="color: var(--accent-green);">✅ All query guard tests passed. No SQL violations detected.</p>'

        return "\n".join(blocks)


def write_html_report(report_data: QueryGuardReportData, output_path: str) -> str:
    """Generate and write an HTML report file. Returns the absolute file path."""
    generator = HTMLReportGenerator(report_data)
    html_content = generator.generate()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path
