"""Read-only repository for approved PostgreSQL student records."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

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


@dataclass(frozen=True)
class StudentDirectoryResult:
    """Paginated approved Student Directory result."""

    students: list[ApprovedStudentRecord]
    total_records: int
    page: int
    per_page: int
    total_pages: int


@dataclass(frozen=True)
class ProgrammeOption:
    """Programme filter option."""

    programme_code: str
    programme_name: str


@dataclass(frozen=True)
class StudentStatusSummary:
    """Approved Student status counts."""

    total: int
    by_status: dict[str, int]


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

    def search_students(
        self,
        *,
        search_term: str = "",
        programme_code: str = "",
        status: str = "",
        page: int = 1,
        per_page: int = 25,
    ) -> StudentDirectoryResult:
        """Return paginated approved student records matching visible fields."""
        where_clauses: list[str] = []
        params: dict[str, str | int] = {
            "limit": per_page,
            "offset": (page - 1) * per_page,
        }

        if search_term:
            where_clauses.append(
                """
                (
                    student_number ILIKE :search_pattern
                    OR first_name ILIKE :search_pattern
                    OR last_name ILIKE :search_pattern
                    OR programme_code ILIKE :search_pattern
                    OR programme_name ILIKE :search_pattern
                )
                """
            )
            params["search_pattern"] = f"%{search_term}%"

        if programme_code:
            where_clauses.append("programme_code = :programme_code")
            params["programme_code"] = programme_code

        if status:
            where_clauses.append("student_status = :status")
            params["status"] = status

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        total_records = db.session.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM {self.schema_name}.vw_student_directory_masked
                {where_sql}
                """
            ),
            params,
        ).scalar_one()

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
                {where_sql}
                ORDER BY student_number
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings()

        total_pages = max(1, ceil(total_records / per_page))
        return StudentDirectoryResult(
            students=[ApprovedStudentRecord(**dict(row)) for row in rows],
            total_records=total_records,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

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

    def list_programmes(self) -> list[ProgrammeOption]:
        """Return available programme filter options."""
        rows = db.session.execute(
            text(
                f"""
                SELECT DISTINCT programme_code, programme_name
                FROM {self.schema_name}.vw_student_directory_masked
                ORDER BY programme_code
                """
            )
        ).mappings()
        return [ProgrammeOption(**dict(row)) for row in rows]

    def list_statuses(self) -> list[str]:
        """Return available approved Student status values."""
        rows = db.session.execute(
            text(
                f"""
                SELECT DISTINCT student_status
                FROM {self.schema_name}.vw_student_directory_masked
                ORDER BY student_status
                """
            )
        ).scalars()
        return [str(status) for status in rows]

    def get_status_summary(self) -> StudentStatusSummary:
        """Return approved Student status counts."""
        rows = db.session.execute(
            text(
                f"""
                SELECT student_status, COUNT(*) AS total
                FROM {self.schema_name}.vw_student_directory_masked
                GROUP BY student_status
                ORDER BY student_status
                """
            )
        ).mappings()
        by_status = {str(row["student_status"]): int(row["total"]) for row in rows}
        return StudentStatusSummary(total=sum(by_status.values()), by_status=by_status)
