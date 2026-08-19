"""
Unit test suite for Phase 4 Step 8 Error Handling & Sensitive Data Sanitization
"""

import pytest
from app.utils.error_handler import (
    sanitize_error_message,
    format_user_friendly_error,
)
from app.services.erp_client import ERPClientError


def test_format_404_not_found():
    msg = format_user_friendly_error(404)
    assert "could not find" in msg.lower()
    assert "student" in msg.lower()


def test_format_403_unauthorized():
    msg = format_user_friendly_error(403)
    assert "access denied" in msg.lower()
    assert "permission" in msg.lower()


def test_format_503_service_unavailable():
    msg = format_user_friendly_error(503)
    assert "unavailable" in msg.lower()


def test_format_504_gateway_timeout():
    msg = format_user_friendly_error(504)
    assert "timed out" in msg.lower()


def test_sanitize_database_credentials():
    raw_error = "FATAL: password authentication failed for user postgresql://postgres:secret123@localhost:5432/xyz_ai"
    sanitized = sanitize_error_message(raw_error)
    assert "secret123" not in sanitized
    assert "postgres" not in sanitized
    assert "internal system error" in sanitized.lower()


def test_sanitize_sql_query_leak():
    raw_error = "SQL syntax error: SELECT password, hash FROM users WHERE id=1"
    sanitized = sanitize_error_message(raw_error)
    assert "SELECT" not in sanitized
    assert "password" not in sanitized
    assert "internal system error" in sanitized.lower()


def test_sanitize_traceback_leak():
    raw_error = "Traceback (most recent call last):\n  File 'app/main.py', line 45 in foo\nValueError: error"
    sanitized = sanitize_error_message(raw_error)
    assert "Traceback" not in sanitized
    assert "internal system error" in sanitized.lower()
