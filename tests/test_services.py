"""Tests for the service layer."""

import pytest

from app.services.student_service import StudentService, StudentValidationError


def test_service_creates_student(app, student_data):
    service = StudentService()
    student = service.create_student(**student_data)

    assert student.first_name == "Ada"
    assert student.student_number == "SR1001"


def test_service_rejects_missing_required_field(app, student_data):
    service = StudentService()
    student_data["email"] = ""

    with pytest.raises(StudentValidationError, match="Email is required."):
        service.create_student(**student_data)


def test_service_rejects_short_name(app, student_data):
    service = StudentService()
    student_data["first_name"] = "A"

    with pytest.raises(
        StudentValidationError, match="First name must be at least 2 characters long."
    ):
        service.create_student(**student_data)


def test_service_rejects_invalid_email(app, student_data):
    service = StudentService()
    student_data["email"] = "not-an-email"

    with pytest.raises(StudentValidationError, match="Email address is invalid."):
        service.create_student(**student_data)


def test_service_rejects_duplicate_student_number(app, student_data):
    service = StudentService()
    service.create_student(**student_data)
    duplicate = student_data | {"email": "other@example.com"}

    with pytest.raises(StudentValidationError, match="Student number already exists."):
        service.create_student(**duplicate)


def test_service_updates_student(app, student, student_data):
    service = StudentService()
    updated = service.update_student(
        student.id,
        **(student_data | {"course": "Data Analytics"}),
    )

    assert updated.course == "Data Analytics"


def test_service_deletes_student(app, student):
    service = StudentService()

    service.delete_student(student.id)

    assert service.get_student(student.id) is None
