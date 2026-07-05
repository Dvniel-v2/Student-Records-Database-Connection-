"""Shared fixtures for application tests."""

import pytest

from app import create_app
from app.extensions import db
from app.services.student_service import StudentService


@pytest.fixture()
def student_data():
    """Return valid student form data."""
    return {
        "student_number": "SR1001",
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "course": "Computer Science",
        "enrolment_date": "2024-09-16",
    }


@pytest.fixture()
def app():
    """Create a Flask app configured for testing."""
    app = create_app("testing")
    app.config.update(TESTING=True)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Provide a test client for HTTP requests."""
    return app.test_client()


@pytest.fixture()
def student(app, student_data):
    """Create a persisted student for tests."""
    return StudentService().create_student(**student_data)
