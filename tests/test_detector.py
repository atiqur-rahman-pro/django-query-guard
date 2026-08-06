"""django-query-guard: Tests for SQL normalization and N+1 pattern detection.

Author: Atiqur Rahman
Role: Software QA Engineer | SDET | Test Automation Architect | Microsoft Contributor | Open Source Contributor
Location: Dhaka, Bangladesh
Email: rahman.atiqur.pro@gmail.com
LinkedIn: https://www.linkedin.com/in/atiqur-rahman-pro
GitHub: https://github.com/atiqur-rahman-pro
License: MIT License
"""

from django_query_guard.detector import NPlusOneDetector, normalize_sql


def test_normalize_sql_numeric_and_string_literals():
    sql1 = "SELECT * FROM user WHERE id = 42 AND name = 'Alice'"
    sql2 = "SELECT * FROM user WHERE id = 99 AND name = 'Bob'"
    assert normalize_sql(sql1) == normalize_sql(sql2)
    assert normalize_sql(sql1) == "SELECT * FROM user WHERE id = ? AND name = ?"


def test_normalize_sql_in_clause():
    sql1 = "SELECT * FROM item WHERE id IN (1, 2, 3)"
    sql2 = "SELECT * FROM item WHERE id IN (4, 5, 6, 7)"
    assert normalize_sql(sql1) == normalize_sql(sql2)
    assert normalize_sql(sql1) == "SELECT * FROM item WHERE id IN (?)"


def test_detector_identifies_n_plus_one_patterns():
    queries = [
        {"sql": "SELECT * FROM user WHERE id = 1"},
        {"sql": "SELECT * FROM profile WHERE user_id = 10"},
        {"sql": "SELECT * FROM profile WHERE user_id = 11"},
        {"sql": "SELECT * FROM profile WHERE user_id = 12"},
    ]
    detector = NPlusOneDetector(threshold=2)
    patterns = detector.analyze(queries)

    assert len(patterns) == 1
    norm_sql = "SELECT * FROM profile WHERE user_id = ?"
    assert norm_sql in patterns
    assert len(patterns[norm_sql]) == 3
