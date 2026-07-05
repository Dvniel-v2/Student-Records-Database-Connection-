"""Tests for the model layer."""

from datetime import date

from app.models.student import Student


def test_student_model_can_be_instantiated():
    student = Student(
        student_number="SR1001",
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        course="Computer Science",
        enrolment_date=date(2024, 9, 16),
    )

    assert student.student_number == "SR1001"
    assert student.first_name == "Ada"
    assert student.to_dict()["enrolment_date"] == "2024-09-16"
