"""Pytest conftest for django-query-guard tests."""

import django
from django.conf import settings

def pytest_configure():
    if not settings.configured:
        settings.configure(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
            ],
            SECRET_KEY="django-query-guard-test-secret-key",
            USE_TZ=True,
        )
        django.setup()
