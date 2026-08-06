"""Tests for query_guard context manager."""

import pytest
from django.db import connection
from django_query_guard.core import query_guard
from django_query_guard.exceptions import NPlusOneQueryError, QueryCountExceededError


@pytest.mark.django_db
def test_query_guard_passes_within_limit():
    with query_guard(max_queries=2, detect_n_plus_one=False):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

    assert True


@pytest.mark.django_db
def test_query_guard_raises_on_count_exceeded():
    with pytest.raises(QueryCountExceededError) as exc_info:
        with query_guard(max_queries=1, detect_n_plus_one=False):
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.execute("SELECT 2")

    assert exc_info.value.executed_count == 2
    assert exc_info.value.max_queries == 1


@pytest.mark.django_db
def test_query_guard_detects_n_plus_one():
    with pytest.raises(NPlusOneQueryError) as exc_info:
        with query_guard(max_queries=10, detect_n_plus_one=True, n_plus_one_threshold=2):
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM auth_user WHERE id = 1")
                cursor.execute("SELECT * FROM auth_user WHERE id = 2")

    assert exc_info.value.count == 2
    assert "SELECT * FROM auth_user WHERE id = ?" in exc_info.value.pattern
