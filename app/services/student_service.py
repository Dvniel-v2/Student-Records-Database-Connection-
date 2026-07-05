"""Service layer for student management."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.student import Student
from app.repositories.student_repository import StudentRepository

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_ENROLMENT_DATE = date(1900, 1, 1)


class StudentValidationError(ValueError):
    """Raised when submitted student data is invalid."""


class StudentServiceError(RuntimeError):
    """Raised when a database operation fails."""


class StudentService:
    """Encapsulate business logic and validation for students."""

    def __init__(self, repository: StudentRepository | None = None) -> None:
        self.repository = repository or StudentRepository()

    def create_student(self, **data: Any) -> Student:
        """Validate and persist a new student."""
        cleaned = self._validate_student_data(data)
        self._ensure_unique_student_number(cleaned["student_number"])
        self._ensure_unique_email(cleaned["email"])

        try:
            student = self.repository.create(**cleaned)
            db.session.commit()
            return student
        except IntegrityError as exc:
            db.session.rollback()
            raise StudentValidationError(
                "Student number or email already exists."
            ) from exc
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise StudentServiceError("Unable to save student.") from exc

    def list_students(self) -> list[Student]:
        """Return all persisted students."""
        return self.repository.list_all()

    def get_student(self, student_id: int) -> Student | None:
        """Return a student by ID."""
        return self.repository.get_by_id(student_id)

    def get_student_by_number(self, student_number: str) -> Student | None:
        """Return a student by student number."""
        return self.repository.get_by_student_number(student_number.strip())

    def update_student(self, student_id: int, **data: Any) -> Student:
        """Validate and update an existing student."""
        student = self.get_student(student_id)
        if student is None:
            raise StudentValidationError("Student not found.")

        cleaned = self._validate_student_data(data)
        self._ensure_unique_student_number(cleaned["student_number"], student.id)
        self._ensure_unique_email(cleaned["email"], student.id)

        try:
            updated_student = self.repository.update(student, **cleaned)
            db.session.commit()
            return updated_student
        except IntegrityError as exc:
            db.session.rollback()
            raise StudentValidationError(
                "Student number or email already exists."
            ) from exc
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise StudentServiceError("Unable to update student.") from exc

    def delete_student(self, student_id: int) -> None:
        """Delete an existing student."""
        student = self.get_student(student_id)
        if student is None:
            raise StudentValidationError("Student not found.")

        try:
            self.repository.delete(student)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise StudentServiceError("Unable to delete student.") from exc

    def _validate_student_data(self, data: dict[str, Any]) -> dict[str, Any]:
        student_number = self._required_text(
            data.get("student_number"), "Student number"
        )
        first_name = self._required_text(data.get("first_name"), "First name")
        last_name = self._required_text(data.get("last_name"), "Last name")
        email = self._required_text(data.get("email"), "Email").lower()
        course = self._required_text(data.get("course"), "Course")
        enrolment_date = self._parse_enrolment_date(data.get("enrolment_date"))

        if len(student_number) > 20:
            raise StudentValidationError(
                "Student number must be 20 characters or fewer."
            )
        self._validate_name(first_name, "First name")
        self._validate_name(last_name, "Last name")
        if len(course) > 120:
            raise StudentValidationError("Course must be 120 characters or fewer.")
        if not EMAIL_RE.match(email):
            raise StudentValidationError("Email address is invalid.")

        return {
            "student_number": student_number,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "course": course,
            "enrolment_date": enrolment_date,
        }

    def _required_text(self, value: Any, label: str) -> str:
        cleaned = str(value or "").strip()
        if not cleaned:
            raise StudentValidationError(f"{label} is required.")
        return cleaned

    def _validate_name(self, value: str, label: str) -> None:
        if len(value) < 2:
            raise StudentValidationError(f"{label} must be at least 2 characters long.")
        if len(value) > 80:
            raise StudentValidationError(f"{label} must be 80 characters or fewer.")

    def _parse_enrolment_date(self, value: Any) -> date:
        if isinstance(value, date):
            enrolment_date = value
        else:
            raw_value = str(value or "").strip()
            if not raw_value:
                raise StudentValidationError("Enrolment date is required.")
            try:
                enrolment_date = datetime.strptime(raw_value, "%Y-%m-%d").date()
            except ValueError as exc:
                raise StudentValidationError(
                    "Enrolment date must be a valid YYYY-MM-DD date."
                ) from exc

        if enrolment_date < MIN_ENROLMENT_DATE:
            raise StudentValidationError("Enrolment date is too far in the past.")
        if enrolment_date > date.today():
            raise StudentValidationError("Enrolment date cannot be in the future.")
        return enrolment_date

    def _ensure_unique_student_number(
        self, student_number: str, current_student_id: int | None = None
    ) -> None:
        existing = self.repository.get_by_student_number(student_number)
        if existing is not None and existing.id != current_student_id:
            raise StudentValidationError("Student number already exists.")

    def _ensure_unique_email(
        self, email: str, current_student_id: int | None = None
    ) -> None:
        existing = self.repository.get_by_email(email)
        if existing is not None and existing.id != current_student_id:
            raise StudentValidationError("Email address already exists.")
