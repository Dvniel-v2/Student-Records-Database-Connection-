"""Service layer for approved academic record pages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.repositories.academic_record_repository import AcademicRecordRepository


class AcademicRecordServiceError(RuntimeError):
    """Raised when approved academic records cannot be read."""


@dataclass(frozen=True)
class RecordPage:
    """Generic read-only record page data."""

    title: str
    subtitle: str
    description: str
    columns: list[tuple[str, str]]
    rows: list[dict[str, Any]]


class AcademicRecordService:
    """Coordinate approved academic record reads."""

    def __init__(self, repository: AcademicRecordRepository | None = None) -> None:
        self.repository = repository or AcademicRecordRepository()

    def courses_page(self) -> RecordPage:
        """Return approved course catalogue page data."""
        try:
            return RecordPage(
                title="Courses",
                subtitle="Approved course catalogue",
                description="Read-only records from the approved PostgreSQL schema.",
                columns=[
                    ("Course code", "course_code"),
                    ("Course name", "course_name"),
                    ("Department", "department_code"),
                    ("Level", "course_level"),
                    ("Credits", "credit_hours"),
                    ("Type", "course_type"),
                    ("Offerings", "offerings"),
                ],
                rows=self.repository.list_courses(),
            )
        except SQLAlchemyError as exc:
            raise AcademicRecordServiceError("Unable to read course records.") from exc

    def modules_page(self) -> RecordPage:
        """Return approved module offering page data."""
        try:
            return RecordPage(
                title="Modules and Course Offerings",
                subtitle="Course offerings by academic term",
                description="Approved course offering records shown as modules.",
                columns=[
                    ("Course code", "course_code"),
                    ("Course name", "course_name"),
                    ("Academic year", "academic_year"),
                    ("Term", "term_name"),
                    ("Section", "section_code"),
                    ("Delivery", "delivery_mode"),
                    ("Capacity", "capacity"),
                    ("Status", "status"),
                ],
                rows=self.repository.list_modules(),
            )
        except SQLAlchemyError as exc:
            raise AcademicRecordServiceError("Unable to read module records.") from exc

    def enrolments_page(self) -> RecordPage:
        """Return approved enrolment page data."""
        try:
            return RecordPage(
                title="Enrolments",
                subtitle="Approved student course registrations",
                description="Read-only records from the approved PostgreSQL schema.",
                columns=[
                    ("Student number", "student_number"),
                    ("Student", "student_name"),
                    ("Course", "course_code"),
                    ("Course name", "course_name"),
                    ("Term", "term_name"),
                    ("Enrolment", "enrolment_status"),
                    ("Result", "result_status"),
                    ("Date", "enrolment_date"),
                ],
                rows=self.repository.list_enrolments(),
            )
        except SQLAlchemyError as exc:
            raise AcademicRecordServiceError(
                "Unable to read enrolment records."
            ) from exc

    def grades_page(self) -> RecordPage:
        """Return approved grade page data."""
        try:
            return RecordPage(
                title="Grades",
                subtitle="Approved assessment records",
                description="Read-only records from the approved PostgreSQL schema.",
                columns=[
                    ("Student number", "student_number"),
                    ("Student", "student_name"),
                    ("Course", "course_code"),
                    ("Assessment", "assessment_type"),
                    ("Numeric grade", "numeric_grade"),
                    ("Letter", "letter_grade"),
                    ("Recorded", "recorded_at"),
                ],
                rows=self.repository.list_grades(),
            )
        except SQLAlchemyError as exc:
            raise AcademicRecordServiceError("Unable to read grade records.") from exc

    def reports(self) -> dict[str, list[dict[str, Any]]]:
        """Return approved reporting view samples."""
        try:
            return self.repository.get_reports()
        except SQLAlchemyError as exc:
            raise AcademicRecordServiceError("Unable to read report records.") from exc
