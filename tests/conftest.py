"""Shared fixtures for application tests."""

import pytest

from app import create_app


@pytest.fixture()
def app():
    """Create a Flask app configured for testing."""
    app = create_app("testing")
    app.config.update(TESTING=True)

    with app.app_context():
        yield app


@pytest.fixture()
def client(app):
    """Provide a test client for HTTP requests."""
    return app.test_client()
