# django-query-guard 🛡️

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/django-query-guard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://pypi.org/project/django-query-guard/)
[![Django Versions](https://img.shields.io/badge/django-4.0%2B-green)](https://djangoproject.com/)
[![Pytest Integration](https://img.shields.io/badge/pytest-supported-brightgreen)](https://docs.pytest.org/)

> **Stop N+1 database queries before they hit production.**  
> `django-query-guard` is an ultra-fast, zero-dependency Python & Pytest plugin that automatically detects N+1 queries and enforces strict query count limits in your Django test suites and backend code.

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

---

## 📦 Installation

Install `django-query-guard` via pip:

```bash
pip install django-query-guard
```

For development and testing with Pytest:

```bash
pip install django-query-guard[dev]
```

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

**Pytest Error Output:**
```text
django_query_guard.exceptions.NPlusOneQueryError: N+1 Query pattern detected! 
Normalized query executed 2 times:
  SELECT * FROM auth_user WHERE id = ?
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

## 🛠️ Custom Exceptions

`django-query-guard` provides explicit exceptions to catch in your application or test suites:

- `QueryGuardError`: Base class for all package exceptions.
- `QueryCountExceededError`: Raised when query count exceeds `max_queries`.
- `NPlusOneQueryError`: Raised when duplicate normalized SQL statements are executed.

---

## 📄 License

This project is licensed under the **MIT License**.

```text
MIT License

Copyright (c) 2026 Atiqur Rahman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO MECHANICAL, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

---

## 🤝 Contributing & Feedback

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](https://github.com/atiqur-rahman-pro/django-query-guard/issues).

Made with ❤️ by [Atiqur Rahman](https://github.com/atiqur-rahman-pro).
