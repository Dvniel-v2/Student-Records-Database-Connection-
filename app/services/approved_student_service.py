"""Service layer for approved PostgreSQL student records."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from app.repositories.approved_student_repository import (
    ApprovedStudentRecord,
    ApprovedStudentRepository,
    ProgrammeOption,
    StudentDirectoryResult,
    StudentStatusSummary,
)


class ApprovedStudentServiceError(RuntimeError):
    """Raised when approved PostgreSQL student data cannot be read."""


class ApprovedStudentValidationError(ValueError):
    """Raised when student query input is invalid."""


class ApprovedStudentService:
    """Return clean read-only student records from the approved schema."""

    PER_PAGE_OPTIONS = (25, 50, 100)
    MAX_SEARCH_LENGTH = 80

    def __init__(self, repository: ApprovedStudentRepository | None = None) -> None:
        self.repository = repository or ApprovedStudentRepository()

    def list_students(self) -> list[ApprovedStudentRecord]:
        """Return student records."""
        try:
            return self.repository.list_students()
        except SQLAlchemyError as exc:
            raise ApprovedStudentServiceError(
                "Unable to read student records."
            ) from exc

    def search_students(
        self,
        *,
        search_term: str = "",
        programme_code: str = "",
        status: str = "",
        page: int = 1,
        per_page: int = 25,
    ) -> StudentDirectoryResult:
        """Return validated and paginated student records."""
        cleaned_search = search_term.strip()[: self.MAX_SEARCH_LENGTH]
        cleaned_programme = programme_code.strip()[:20]
        cleaned_status = status.strip()[:40]
        cleaned_page = max(page, 1)
        cleaned_per_page = per_page if per_page in self.PER_PAGE_OPTIONS else 25

        try:
            result = self.repository.search_students(
                search_term=cleaned_search,
                programme_code=cleaned_programme,
                status=cleaned_status,
                page=cleaned_page,
                per_page=cleaned_per_page,
            )
            if cleaned_page > result.total_pages:
                return self.repository.search_students(
                    search_term=cleaned_search,
                    programme_code=cleaned_programme,
                    status=cleaned_status,
                    page=result.total_pages,
                    per_page=cleaned_per_page,
                )
            return result
        except SQLAlchemyError as exc:
            raise ApprovedStudentServiceError(
                "Unable to read student records."
            ) from exc

    def get_student(self, student_id: int) -> ApprovedStudentRecord | None:
        """Return one student record."""
        if student_id < 1:
            raise ApprovedStudentValidationError("Student id must be positive.")

        try:
            return self.repository.get_student(student_id)
        except SQLAlchemyError as exc:
            raise ApprovedStudentServiceError("Unable to read student record.") from exc

    def list_programmes(self) -> list[ProgrammeOption]:
        """Return programme options for Student Directory filters."""
        try:
            return self.repository.list_programmes()
        except SQLAlchemyError as exc:
            raise ApprovedStudentServiceError(
                "Unable to read approved programme filters."
            ) from exc

    def list_statuses(self) -> list[str]:
        """Return student status filter values."""
        try:
            return self.repository.list_statuses()
        except SQLAlchemyError as exc:
            raise ApprovedStudentServiceError(
                "Unable to read approved status filters."
            ) from exc

    def get_status_summary(self) -> StudentStatusSummary:
        """Return student status summary counts."""
        try:
            return self.repository.get_status_summary()
        except SQLAlchemyError as exc:
            raise ApprovedStudentServiceError(
                "Unable to read student summary."
            ) from exc
