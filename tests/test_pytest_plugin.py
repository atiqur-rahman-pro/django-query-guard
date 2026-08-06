"""Tests for Pytest marker integration."""

import pytest
from django.db import connection
from django_query_guard.core import query_guard
from django_query_guard.exceptions import NPlusOneQueryError, QueryCountExceededError


@pytest.mark.django_db
@pytest.mark.query_guard(max_queries=2, detect_n_plus_one=False)
def test_pytest_marker_within_limit():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    assert True


@pytest.mark.django_db
def test_query_guard_context_manager_in_pytest():
    with pytest.raises(QueryCountExceededError):
        with query_guard(max_queries=1):
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.execute("SELECT 2")


@pytest.mark.django_db
def test_query_guard_n_plus_one_in_pytest():
    with pytest.raises(NPlusOneQueryError):
        with query_guard(max_queries=10, detect_n_plus_one=True, n_plus_one_threshold=2):
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM auth_user WHERE id = 10")
                cursor.execute("SELECT * FROM auth_user WHERE id = 20")
