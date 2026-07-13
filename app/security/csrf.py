"""Small CSRF helper for server-rendered forms."""

from __future__ import annotations

import secrets

from flask import abort, current_app, request, session

CSRF_SESSION_KEY = "_csrf_token"


def csrf_token() -> str:
    """Return the session CSRF token, creating it when needed."""
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return str(token)


def validate_csrf() -> None:
    """Reject unsafe form posts without a valid CSRF token."""
    if not current_app.config.get("CSRF_ENABLED", True):
        return
    expected = session.get(CSRF_SESSION_KEY)
    received = request.form.get("csrf_token", "")
    if not expected or not secrets.compare_digest(str(expected), received):
        abort(400, description="Invalid CSRF token.")
