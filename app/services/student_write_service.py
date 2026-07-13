"""Service layer for approved PostgreSQL Student write workflows."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.repositories.approved_student_repository import ProgrammeOption
from app.repositories.student_write_repository import (
    EditableStudentRecord,
    StudentWriteRepository,
)

ADMISSION_TYPES = ("Local", "International", "Exchange")
STUDENT_STATUSES = ("Active", "Suspended", "Withdrawn", "Graduated")
GRADUATION_STATUSES = ("Not eligible", "Eligible", "Graduated")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class StudentWriteValidationError(ValueError):
    """Raised when Student form data is invalid."""

    def __init__(self, errors: dict[str, str]) -> None:
        super().__init__("Student form validation failed.")
        self.errors = errors


class StudentWriteConflictError(RuntimeError):
    """Raised when a Student write conflicts with existing records."""


class StudentWriteServiceError(RuntimeError):
    """Raised when a Student write cannot be completed."""


@dataclass(frozen=True)
class StudentFormChoices:
    """Reference choices for Student forms."""

    programmes: list[ProgrammeOption]
    admission_types: tuple[str, ...] = ADMISSION_TYPES
    student_statuses: tuple[str, ...] = STUDENT_STATUSES
    graduation_statuses: tuple[str, ...] = GRADUATION_STATUSES


class StudentWriteService:
    """Validate and coordinate Student writes."""

    def __init__(self, repository: StudentWriteRepository | None = None) -> None:
        self.repository = repository or StudentWriteRepository()

    def form_choices(self) -> StudentFormChoices:
        """Return form reference values from PostgreSQL and schema constants."""
        try:
            return StudentFormChoices(programmes=self.repository.list_programmes())
        except SQLAlchemyError as exc:
            raise StudentWriteServiceError(
                "Unable to load Student form reference data."
            ) from exc

    def get_student_for_edit(self, student_id: int) -> EditableStudentRecord | None:
        """Return editable Student details."""
        try:
            return self.repository.get_student_for_edit(student_id)
        except SQLAlchemyError as exc:
            raise StudentWriteServiceError("Unable to load Student details.") from exc

    def create_student(self, form: dict[str, Any]) -> int:
        """Validate and create a Student."""
        data = self._clean(form, require_email=True)
        self._raise_if_invalid(data, require_email=True)
        try:
            self._check_conflicts(data)
            return self.repository.create_student(data)
        except StudentWriteConflictError:
            raise
        except LookupError as exc:
            raise StudentWriteValidationError(
                {"programme_code": "The selected programme is no longer available."}
            ) from exc
        except IntegrityError as exc:
            raise StudentWriteConflictError(
                "A Student with this number or email already exists."
            ) from exc
        except SQLAlchemyError as exc:
            raise StudentWriteServiceError("Unable to create Student record.") from exc

    def update_student(self, student_id: int, form: dict[str, Any]) -> None:
        """Validate and update a Student."""
        current = self.get_student_for_edit(student_id)
        if current is None:
            raise StudentWriteValidationError({"student": "Student not found."})
        data = self._clean(form, require_email=False)
        self._raise_if_invalid(data, require_email=False)
        try:
            self._check_conflicts(
                data,
                exclude_student_id=student_id,
                exclude_person_id=current.person_id,
            )
            self.repository.update_student(student_id, data)
        except StudentWriteConflictError:
            raise
        except LookupError as exc:
            raise StudentWriteValidationError(
                {"programme_code": "The selected programme is no longer available."}
            ) from exc
        except IntegrityError as exc:
            raise StudentWriteConflictError(
                "A Student with this number or email already exists."
            ) from exc
        except SQLAlchemyError as exc:
            raise StudentWriteServiceError("Unable to update Student record.") from exc

    def withdraw_student(self, student_id: int) -> None:
        """Withdraw a Student instead of deleting academic history."""
        try:
            self.repository.withdraw_student(student_id)
        except LookupError as exc:
            raise StudentWriteValidationError(
                {"student": "Student not found."}
            ) from exc
        except SQLAlchemyError as exc:
            raise StudentWriteServiceError(
                "Unable to withdraw Student record."
            ) from exc

    def _check_conflicts(
        self,
        data: dict[str, Any],
        *,
        exclude_student_id: int | None = None,
        exclude_person_id: int | None = None,
    ) -> None:
        if self.repository.student_number_exists(
            data["student_number"], exclude_student_id
        ):
            raise StudentWriteConflictError(
                "A Student with this number already exists."
            )
        if data.get("email") and self.repository.email_exists(
            data["email"], exclude_person_id
        ):
            raise StudentWriteConflictError("A Student with this email already exists.")

    def _clean(self, form: dict[str, Any], *, require_email: bool) -> dict[str, Any]:
        email = str(form.get("email", "")).strip().lower()
        if not require_email and not email:
            email = ""
        return {
            "student_number": str(form.get("student_number", "")).strip().upper(),
            "first_name": str(form.get("first_name", "")).strip(),
            "last_name": str(form.get("last_name", "")).strip(),
            "email": email,
            "phone": str(form.get("phone", "")).strip() or None,
            "nationality": str(form.get("nationality", "")).strip() or None,
            "programme_code": str(form.get("programme_code", "")).strip(),
            "date_of_birth": str(form.get("date_of_birth", "")).strip(),
            "enrolment_year": str(form.get("enrolment_year", "")).strip(),
            "year_of_study": str(form.get("year_of_study", "")).strip(),
            "admission_type": str(form.get("admission_type", "")).strip(),
            "student_status": str(form.get("student_status", "")).strip() or "Active",
            "graduation_status": (
                str(form.get("graduation_status", "")).strip() or "Not eligible"
            ),
        }

    def _raise_if_invalid(self, data: dict[str, Any], *, require_email: bool) -> None:
        errors: dict[str, str] = {}
        self._require_length(errors, data, "student_number", "Student number", 3, 30)
        self._require_length(errors, data, "first_name", "First name", 1, 60)
        self._require_length(errors, data, "last_name", "Last name", 1, 60)
        if require_email or data.get("email"):
            if not EMAIL_PATTERN.match(str(data.get("email", ""))):
                errors["email"] = "Enter a valid email address."
        if not data["programme_code"]:
            errors["programme_code"] = "Select a programme."
        self._validate_date(errors, data)
        self._validate_int(errors, data, "enrolment_year", "Enrolment year", 2000, 2100)
        self._validate_int(errors, data, "year_of_study", "Year of study", 1, 8)
        self._validate_choice(errors, data, "admission_type", ADMISSION_TYPES)
        self._validate_choice(errors, data, "student_status", STUDENT_STATUSES)
        self._validate_choice(errors, data, "graduation_status", GRADUATION_STATUSES)
        if errors:
            raise StudentWriteValidationError(errors)

    def _require_length(
        self,
        errors: dict[str, str],
        data: dict[str, Any],
        field: str,
        label: str,
        min_length: int,
        max_length: int,
    ) -> None:
        value = str(data.get(field, ""))
        if len(value) < min_length:
            errors[field] = f"{label} is required."
        elif len(value) > max_length:
            errors[field] = f"{label} must be {max_length} characters or fewer."

    def _validate_date(self, errors: dict[str, str], data: dict[str, Any]) -> None:
        try:
            parsed = date.fromisoformat(str(data["date_of_birth"]))
        except ValueError:
            errors["date_of_birth"] = "Enter a valid date of birth."
            return
        if parsed >= date.today():
            errors["date_of_birth"] = "Date of birth must be in the past."

    def _validate_int(
        self,
        errors: dict[str, str],
        data: dict[str, Any],
        field: str,
        label: str,
        minimum: int,
        maximum: int,
    ) -> None:
        try:
            value = int(data[field])
        except (TypeError, ValueError):
            errors[field] = f"{label} must be a number."
            return
        if not minimum <= value <= maximum:
            errors[field] = f"{label} must be between {minimum} and {maximum}."
            return
        data[field] = value

    def _validate_choice(
        self,
        errors: dict[str, str],
        data: dict[str, Any],
        field: str,
        choices: tuple[str, ...],
    ) -> None:
        if data[field] not in choices:
            errors[field] = "Select a valid option."
