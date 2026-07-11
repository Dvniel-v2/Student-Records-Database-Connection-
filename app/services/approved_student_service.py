"""Service layer for approved PostgreSQL student records."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from app.repositories.approved_student_repository import (
    ApprovedStudentRecord,
    ApprovedStudentRepository,
)


class ApprovedStudentServiceError(RuntimeError):
    """Raised when approved PostgreSQL student data cannot be read."""


class ApprovedStudentValidationError(ValueError):
    """Raised when approved student query input is invalid."""


class ApprovedStudentService:
    """Return clean read-only student records from the approved schema."""

    def __init__(self, repository: ApprovedStudentRepository | None = None) -> None:
        self.repository = repository or ApprovedStudentRepository()

    def list_students(self) -> list[ApprovedStudentRecord]:
        """Return approved student records."""
        try:
            return self.repository.list_students()
        except SQLAlchemyError as exc:
            raise ApprovedStudentServiceError(
                "Unable to read approved student records."
            ) from exc

    def get_student(self, student_id: int) -> ApprovedStudentRecord | None:
        """Return one approved student record."""
        if student_id < 1:
            raise ApprovedStudentValidationError("Student id must be positive.")

        try:
            return self.repository.get_student(student_id)
        except SQLAlchemyError as exc:
            raise ApprovedStudentServiceError(
                "Unable to read approved student record."
            ) from exc
