"""
XYZ AI Backend — Error Handling & Sanitization Utility

Provides centralized, user-safe error translation and sanitization.
Guarantees that raw stack traces, SQL queries, database credentials,
and internal API keys are NEVER exposed to the end user.
"""

from typing import Dict, Any, Optional
import logging
import re

logger = logging.getLogger("app.utils.error_handler")

# Patterns for sensitive data that must never be exposed
SENSITIVE_PATTERNS = [
    re.compile(r"postgres(ql)?://[^\s]+", re.IGNORECASE),
    re.compile(r"password\s*=\s*[^\s,]+", re.IGNORECASE),
    re.compile(r"secret[_\s]*key\s*=\s*[^\s,]+", re.IGNORECASE),
    re.compile(r"api[_\s]*key\s*=\s*[^\s,]+", re.IGNORECASE),
    re.compile(r"SELECT\s+.*\s+FROM", re.IGNORECASE),
    re.compile(r"Traceback \(most recent call last\):", re.IGNORECASE),
]


def sanitize_error_message(raw_error: str) -> str:
    """
    Strips internal database queries, credentials, and tracebacks from error strings.
    """
    if not raw_error:
        return "An unexpected error occurred. Please try again."
        
    sanitized = raw_error
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(sanitized):
            logger.warning(f"Sanitizer blocked sensitive leak in error: {sanitized}")
            return "An internal system error occurred. Please contact school administration if this persists."
            
    return sanitized


def format_user_friendly_error(status_code: int, detail: Optional[str] = None) -> str:
    """
    Translates HTTP / ERP status codes into clear, polite, actionable user messages.
    """
    if status_code == 404:
        return "I could not find the requested student or attendance record in the school system."
    elif status_code == 403:
        return "Access denied. You do not have permission to view or perform this action."
    elif status_code == 400:
        clean_detail = sanitize_error_message(detail or "Invalid request parameters.")
        return f"Invalid request: {clean_detail}"
    elif status_code == 503:
        return "The school ERP system is currently unavailable. Please try again in a few moments."
    elif status_code == 504:
        return "The request to the school system timed out. Please check your connection and try again."
    elif status_code >= 500:
        return "The school system encountered an internal error. Please try again shortly."
        
    return sanitize_error_message(detail or "An error occurred while processing your request.")
