# django-query-guard 🛡️

### Created by:
**Atiqur Rahman**  
*Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor*  
📍 Dhaka, Bangladesh | ✉️ [rahman.atiqur.pro@gmail.com](mailto:rahman.atiqur.pro@gmail.com) | 🌐 [LinkedIn](https://www.linkedin.com/in/atiqur-rahman-pro) | 🐙 [GitHub Profile](https://github.com/atiqur-rahman-pro)

---

[![PyPI version](https://img.shields.io/badge/pypi-v0.2.0-blue.svg)](https://pypi.org/project/django-query-guard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://pypi.org/project/django-query-guard/)
[![Django Versions](https://img.shields.io/badge/django-4.0%2B-green)](https://djangoproject.com/)
[![Pytest Integration](https://img.shields.io/badge/pytest-supported-brightgreen)](https://docs.pytest.org/)

> **Stop N+1 database queries before they hit production.**  
> `django-query-guard` is an ultra-fast, zero-dependency Python & Pytest plugin that automatically detects N+1 queries and enforces strict query count limits in your Django test suites and backend code.

---

## 📦 Installation (2 Ways to Install)

You can install `django-query-guard` using either of the two official methods below:

### 1️⃣ Standard Installation via PyPI (Recommended)

Install the official stable package directly from the [PyPI Repository](https://pypi.org/project/django-query-guard/):

```bash
pip install django-query-guard
```

For development and testing tools (Pytest & Pytest-Django):
```bash
pip install django-query-guard[dev]
```

### 2️⃣ Direct Installation via GitHub (Latest Bleeding-Edge Version)

Install the latest main branch version directly from the [GitHub Source Repository](https://github.com/atiqur-rahman-pro/django-query-guard):

```bash
pip install git+https://github.com/atiqur-rahman-pro/django-query-guard.git
```

---

## 💡 Why Django Developers Need This

In Django, the ORM makes database queries so easy that it’s terrifyingly easy to accidentally write **N+1 queries**:

```python
# ❌ THE N+1 ACCIDENT
# Fetches 100 users, then executes 100 individual queries for each profile!
# Total: 101 Database Queries! 🐌
users = User.objects.all()
profiles = [user.profile.bio for user in users]
```

### The Solution: `django-query-guard`

Instead of relying on manual code reviews or checking server logs, `django-query-guard` turns query limits and N+1 prevention into **automated, enforceable CI/CD tests**:

```python
# ✅ THE SOLUTION
import pytest

@pytest.mark.django_db
@pytest.mark.query_guard(max_queries=2, detect_n_plus_one=True)
def test_user_profiles_api(client):
    response = client.get("/api/users/")
    assert response.status_code == 200
```

If your endpoint accidentally runs 101 queries instead of 2, **Pytest fails instantly** with an exact breakdown of which query repeated! 💥

---

## 🔥 Key Features

- 🎯 **Pytest Marker Integration**: Simple `@pytest.mark.query_guard(max_queries=N)`.
- 🧠 **Smart SQL Normalization**: Normalizes SQL queries (e.g. `WHERE id = 1` and `WHERE id = 2` are recognized as the exact same query pattern).
- 🛡️ **Zero Heavy Dependencies**: Built purely on Django's native database execution wrapper and standard library.
- ⚡ **Ultra-Fast**: Sub-millisecond execution overhead (< 1ms per test).
- 🐍 **Python 3.10+ & Django 4.0+ Compatible**: Works out-of-the-box with all modern Django versions.
- 📊 **HTML Report Generation**: Beautiful dark-themed HTML reports with summary cards, test results table, and SQL query details.
- 🔔 **CI/CD GitHub Actions Ready**: Ready-made workflow template for automatic N+1 detection on every Pull Request.
- 📈 **Query Count Trend Tracking**: JSON-based run history with regression/improvement detection across Pytest runs.

---

## 📖 A to Z Guide: How to Use

### 1. Using `@pytest.mark.query_guard` in Pytest

Simply decorate any test function that accesses the database:

```python
import pytest

@pytest.mark.django_db
@pytest.mark.query_guard(max_queries=3)
def test_fetch_dashboard_data(client):
    response = client.get("/api/dashboard/")
    assert response.status_code == 200
```

#### Parameters for `query_guard` Marker:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `max_queries` | `int` | `None` | Maximum allowed total SQL queries. Raises `QueryCountExceededError` if exceeded. |
| `detect_n_plus_one` | `bool` | `True` | Automatically detect N+1 query patterns. |
| `n_plus_one_threshold` | `int` | `2` | Minimum repetitions of a normalized query required to trigger N+1 detection. |

---

### 2. Strict N+1 Detection Mode

Even if your total query count is under `max_queries`, a loop executing duplicate queries will trigger an `NPlusOneQueryError`:

```python
@pytest.mark.django_db
@pytest.mark.query_guard(detect_n_plus_one=True, n_plus_one_threshold=2)
def test_user_loop():
    # Executes SELECT * FROM auth_user WHERE id = ? twice
    for user_id in [10, 20]:
        User.objects.get(id=user_id)
```

---

### 3. Using as a Context Manager (`with query_guard(...)`)

You can also use `query_guard` directly inside Django views, Celery tasks, management commands, or standard unit tests:

```python
from django_query_guard import query_guard, NPlusOneQueryError

def process_latest_orders():
    with query_guard(max_queries=5, detect_n_plus_one=True):
        orders = Order.objects.filter(status="pending").select_related("user")
        for order in orders:
            print(order.user.email)
```

---

### 4. How to Fix Detected N+1 Queries in Django

When `django-query-guard` catches an N+1 query, fix it using Django's ORM optimization methods:

#### Fix 1: Use `select_related` for Foreign Keys (One-to-One / Many-to-One)
```python
# ❌ Before (N+1 Queries)
books = Book.objects.all()
authors = [book.author.name for book in books]

# ✅ After (1 Query via JOIN)
books = Book.objects.select_related("author").all()
authors = [book.author.name for book in books]
```

#### Fix 2: Use `prefetch_related` for Reverse Foreign Keys / Many-to-Many
```python
# ❌ Before (N+1 Queries)
authors = Author.objects.all()
books = [author.books.all() for author in authors]

# ✅ After (2 Queries Total)
authors = Author.objects.prefetch_related("books").all()
books = [author.books.all() for author in authors]
```

---

## 📊 HTML Report Generation (New in v0.2.0)

Generate a premium dark-themed HTML report after every Pytest run:

```bash
pytest --query-guard-report=report.html
```

The report includes:
- **Summary Cards**: Total tests, passed/failed counts, total queries, and N+1 detections at a glance.
- **Test Results Table**: Per-test query count, max allowed, N+1 status, and duration.
- **SQL Query Details**: Full SQL breakdown for failed tests with exact query text and execution time.

---

## 📈 Query Count Trend Tracking (New in v0.2.0)

Track query performance across multiple Pytest runs with automatic regression detection:

```bash
pytest --query-guard-trend=.query_guard_history.json
```

Terminal output after each run:
```text
========================================================================
===================== QUERY GUARD TREND COMPARISON =====================
========================================================================
  Current Run:  3 queries across 5 tests
  Previous Run: 30 queries across 5 tests

  [IMPROVEMENT] Query Delta: -27 queries
========================================================================
```

Combine both flags for full reporting:
```bash
pytest --query-guard-report=report.html --query-guard-trend=.query_guard_history.json
```

---

## 🔔 CI/CD GitHub Actions Integration (New in v0.2.0)

Copy the ready-made workflow file to your project:

```bash
mkdir -p .github/workflows
cp query_guard_ci.yml .github/workflows/
```

Or add to your existing workflow:

```yaml
- name: Run Query Guard Tests
  run: |
    pip install django-query-guard
    pytest --query-guard-report=report.html --query-guard-trend=.query_guard_history.json -v

- name: Upload Query Guard Report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: query-guard-report
    path: report.html
```

This ensures **every Pull Request is automatically checked** for N+1 query regressions before merging!

---

## 🛠️ Custom Exceptions

`django-query-guard` provides explicit exceptions to catch in your application or test suites:

- `QueryGuardError`: Base class for all package exceptions.
- `QueryCountExceededError`: Raised when query count exceeds `max_queries`.
- `NPlusOneQueryError`: Raised when duplicate normalized SQL statements are executed.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👤 Author & Maintainer

**Atiqur Rahman**  
*Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor*  
📍 Dhaka, Bangladesh | ✉️ [rahman.atiqur.pro@gmail.com](mailto:rahman.atiqur.pro@gmail.com) | 🌐 [LinkedIn](https://www.linkedin.com/in/atiqur-rahman-pro) | 🐙 [GitHub Profile](https://github.com/atiqur-rahman-pro)
