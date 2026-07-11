"""Tests for approved PostgreSQL student service behaviour."""

import pytest

from app.repositories.approved_student_repository import ApprovedStudentRecord
from app.services.approved_student_service import (
    ApprovedStudentService,
    ApprovedStudentValidationError,
)


class FakeApprovedStudentRepository:
    """Fake repository for approved student service tests."""

    def list_students(self):
        return [
            ApprovedStudentRecord(
                student_id=1,
                student_number="USE1001",
                first_name="Ada",
                last_name="Lovelace",
                masked_email="ad***@use.edu",
                programme_code="UB-CSC",
                programme_name="B.Sc. Computer Science",
                enrolment_year=2024,
                year_of_study=1,
                student_status="Active",
                graduation_status="Not eligible",
            )
        ]

    def get_student(self, student_id: int):
        return self.list_students()[0] if student_id == 1 else None


def test_approved_student_service_lists_students():
    service = ApprovedStudentService(FakeApprovedStudentRepository())

    students = service.list_students()

    assert students[0].student_number == "USE1001"
    assert students[0].programme_code == "UB-CSC"


def test_approved_student_service_gets_student():
    service = ApprovedStudentService(FakeApprovedStudentRepository())

    student = service.get_student(1)

    assert student is not None
    assert student.masked_email == "ad***@use.edu"


def test_approved_student_service_rejects_invalid_id():
    service = ApprovedStudentService(FakeApprovedStudentRepository())

    with pytest.raises(
        ApprovedStudentValidationError, match="Student id must be positive."
    ):
        service.get_student(0)
