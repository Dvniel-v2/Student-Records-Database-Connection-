"""Tests for Student write service validation and coordination."""

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.approved_student_repository import ProgrammeOption
from app.repositories.student_write_repository import EditableStudentRecord
from app.services.student_write_service import (
    StudentWriteConflictError,
    StudentWriteService,
    StudentWriteServiceError,
    StudentWriteValidationError,
)


def _valid_form():
    return {
        "student_number": "use-test-0001",
        "first_name": "Grace",
        "last_name": "Hopper",
        "email": "grace@stu.use.edu",
        "phone": "+44 100",
        "nationality": "British",
        "programme_code": "UB-CSC",
        "date_of_birth": "2001-01-01",
        "enrolment_year": "2024",
        "year_of_study": "1",
        "admission_type": "Local",
        "student_status": "Active",
        "graduation_status": "Not eligible",
    }


def _editable_student():
    return EditableStudentRecord(
        student_id=1,
        person_id=10,
        student_number="USE-TEST-0001",
        first_name="Grace",
        last_name="Hopper",
        masked_email="gr***@stu.use.edu",
        phone="+44 100",
        nationality="British",
        programme_code="UB-CSC",
        programme_name="B.Sc. Computer Science",
        date_of_birth="2001-01-01",
        enrolment_year=2024,
        year_of_study=1,
        admission_type="Local",
        student_status="Active",
        graduation_status="Not eligible",
    )


class FakeRepository:
    """Repository fake for Student write service tests."""

    def __init__(self):
        self.student_number_conflict = False
        self.email_conflict = False
        self.create_error = None
        self.update_error = None
        self.withdraw_error = None
        self.created_data = None
        self.updated_data = None
        self.withdrawn_id = None

    def list_programmes(self):
        return [ProgrammeOption("UB-CSC", "B.Sc. Computer Science")]

    def get_student_for_edit(self, student_id: int):
        if student_id == 1:
            return _editable_student()
        return None

    def student_number_exists(self, student_number, exclude_student_id=None):
        return self.student_number_conflict

    def email_exists(self, email, exclude_person_id=None):
        return self.email_conflict

    def create_student(self, data):
        self.created_data = data
        if self.create_error:
            raise self.create_error
        return 1

    def update_student(self, student_id, data):
        self.updated_data = data
        if self.update_error:
            raise self.update_error

    def withdraw_student(self, student_id):
        self.withdrawn_id = student_id
        if self.withdraw_error:
            raise self.withdraw_error


def test_create_student_normalises_and_saves_valid_data():
    repo = FakeRepository()
    service = StudentWriteService(repo)

    student_id = service.create_student(_valid_form())

    assert student_id == 1
    assert repo.created_data["student_number"] == "USE-TEST-0001"
    assert repo.created_data["enrolment_year"] == 2024
    assert repo.created_data["year_of_study"] == 1


def test_create_student_rejects_invalid_data():
    service = StudentWriteService(FakeRepository())
    form = _valid_form()
    form["email"] = "bad-email"
    form["year_of_study"] = "99"

    with pytest.raises(StudentWriteValidationError) as exc:
        service.create_student(form)

    assert "email" in exc.value.errors
    assert "year_of_study" in exc.value.errors


def test_create_student_reports_duplicate_student_number():
    repo = FakeRepository()
    repo.student_number_conflict = True
    service = StudentWriteService(repo)

    with pytest.raises(StudentWriteConflictError):
        service.create_student(_valid_form())


def test_update_student_allows_blank_email_to_preserve_masked_email():
    repo = FakeRepository()
    service = StudentWriteService(repo)
    form = _valid_form()
    form["email"] = ""

    service.update_student(1, form)

    assert repo.updated_data["email"] == ""


def test_update_student_reports_repository_failure_safely():
    repo = FakeRepository()
    repo.update_error = SQLAlchemyError("raw database error")
    service = StudentWriteService(repo)

    with pytest.raises(StudentWriteServiceError):
        service.update_student(1, _valid_form())


def test_withdraw_student_calls_repository_lifecycle_update():
    repo = FakeRepository()
    service = StudentWriteService(repo)

    service.withdraw_student(1)

    assert repo.withdrawn_id == 1
