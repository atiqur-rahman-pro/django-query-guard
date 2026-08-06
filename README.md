# django-query-guard 🛡️

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/django-query-guard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://pypi.org/project/django-query-guard/)
[![Django Versions](https://img.shields.io/badge/django-4.0%2B-green)](https://djangoproject.com/)

**django-query-guard** is a lightweight, zero-dependency Python library and Pytest plugin designed to detect and prevent N+1 queries and database query bloat in Django applications.

---

## ⚡ Key Features

- 🎯 **Pytest Integration**: Decorate tests with `@pytest.mark.query_guard(max_queries=N)`.
- 🔍 **N+1 Query Pattern Detection**: Automatically normalizes SQL queries and pinpoints repeated query signatures.
- 📦 **Context Manager Support**: Use `with query_guard(max_queries=N):` in Django views, tasks, or scripts.
- 🚀 **Zero Heavy Dependencies**: Built purely on Django's connection hooks and Python's standard library.

---

## 📦 Installation

```bash
pip install django-query-guard
```

---

## 🚀 Quickstart & Usage

### 1. Pytest Marker Usage

```python
import pytest
from django_query_guard import query_guard

@pytest.mark.query_guard(max_queries=3, detect_n_plus_one=True)
def test_user_list_api(client):
    response = client.get("/api/users/")
    assert response.status_code == 200
```

If the endpoint executes more than 3 database queries or triggers an N+1 pattern, Pytest fails immediately with a detailed query breakdown!

### 2. Context Manager Usage

```python
from django_query_guard import query_guard, QueryCountExceededError, NPlusOneQueryError

def process_orders():
    with query_guard(max_queries=10, detect_n_plus_one=True):
        # Your Django ORM calls here
        orders = Order.objects.filter(status="pending").select_related("user")
        for order in orders:
            order.mark_processed()
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
