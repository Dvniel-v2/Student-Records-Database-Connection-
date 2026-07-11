"""Read-only repository for approved PostgreSQL student records."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text

from app.config import APPROVED_DATABASE_SCHEMA
from app.extensions import db


@dataclass(frozen=True)
class ApprovedStudentRecord:
    """Student data exposed from the approved normalised PostgreSQL schema."""

    student_id: int
    student_number: str
    first_name: str
    last_name: str
    masked_email: str
    programme_code: str
    programme_name: str
    enrolment_year: int
    year_of_study: int
    student_status: str
    graduation_status: str

    @property
    def id(self) -> int:
        """Compatibility alias for existing route and template patterns."""
        return self.student_id

    @property
    def course(self) -> str:
        """Compatibility alias until templates fully adopt programme wording."""
        return self.programme_name

    @property
    def email(self) -> str:
        """Compatibility alias for the masked institutional email."""
        return self.masked_email

    @property
    def enrolment_date(self) -> str:
        """Compatibility text for the approved enrolment year field."""
        return str(self.enrolment_year)


class ApprovedStudentRepository:
    """Query approved PostgreSQL student records without legacy ORM models."""

    def __init__(self, schema_name: str = APPROVED_DATABASE_SCHEMA) -> None:
        self.schema_name = schema_name

    def list_students(self) -> list[ApprovedStudentRecord]:
        """Return approved student directory records ordered by student number."""
        rows = db.session.execute(
            text(
                f"""
                SELECT
                    student_id,
                    student_number,
                    first_name,
                    last_name,
                    masked_email,
                    programme_code,
                    programme_name,
                    enrolment_year,
                    year_of_study,
                    student_status,
                    graduation_status
                FROM {self.schema_name}.vw_student_directory_masked
                ORDER BY student_number
                """
            )
        ).mappings()
        return [ApprovedStudentRecord(**dict(row)) for row in rows]

    def get_student(self, student_id: int) -> ApprovedStudentRecord | None:
        """Return one approved student directory record by student id."""
        row = (
            db.session.execute(
                text(
                    f"""
                SELECT
                    student_id,
                    student_number,
                    first_name,
                    last_name,
                    masked_email,
                    programme_code,
                    programme_name,
                    enrolment_year,
                    year_of_study,
                    student_status,
                    graduation_status
                FROM {self.schema_name}.vw_student_directory_masked
                WHERE student_id = :student_id
                """
                ),
                {"student_id": student_id},
            )
            .mappings()
            .first()
        )

        if row is None:
            return None
        return ApprovedStudentRecord(**dict(row))
