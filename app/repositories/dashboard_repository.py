"""Repository for approved PostgreSQL dashboard reads."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text

from app.config import APPROVED_DATABASE_SCHEMA
from app.extensions import db
from app.repositories.approved_student_repository import ApprovedStudentRecord


@dataclass(frozen=True)
class DashboardMetrics:
    """Real dashboard metrics from approved PostgreSQL tables."""

    total_students: int
    active_programmes: int
    current_enrolments: int
    results_in_progress: int


@dataclass(frozen=True)
class DashboardBar:
    """Single dashboard chart bar."""

    label: str
    value: int
    percentage: int


class DashboardRepository:
    """Read approved dashboard data without route-level SQL."""

    def __init__(self, schema_name: str = APPROVED_DATABASE_SCHEMA) -> None:
        self.schema_name = schema_name

    def get_metrics(self) -> DashboardMetrics:
        """Return real dashboard metric counts."""
        row = (
            db.session.execute(
                text(
                    f"""
                SELECT
                    (SELECT COUNT(*) FROM {self.schema_name}.student)
                        AS total_students,
                    (SELECT COUNT(*) FROM {self.schema_name}.programme
                     WHERE is_active IS TRUE) AS active_programmes,
                    (SELECT COUNT(*) FROM {self.schema_name}.enrolment
                     WHERE enrolment_status = 'Enrolled') AS current_enrolments,
                    (SELECT COUNT(*) FROM {self.schema_name}.enrolment
                     WHERE result_status = 'In progress') AS results_in_progress
                """
                )
            )
            .mappings()
            .one()
        )
        return DashboardMetrics(
            total_students=int(row["total_students"]),
            active_programmes=int(row["active_programmes"]),
            current_enrolments=int(row["current_enrolments"]),
            results_in_progress=int(row["results_in_progress"]),
        )

    def get_student_overview(self, limit: int = 6) -> list[ApprovedStudentRecord]:
        """Return a small approved Student overview for the dashboard."""
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
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings()
        return [ApprovedStudentRecord(**dict(row)) for row in rows]

    def get_student_status_bars(self) -> list[DashboardBar]:
        """Return Student status distribution bars from approved data."""
        rows = db.session.execute(
            text(
                f"""
                SELECT student_status AS label, COUNT(*) AS value
                FROM {self.schema_name}.vw_student_directory_masked
                GROUP BY student_status
                ORDER BY value DESC, student_status
                """
            )
        ).mappings()
        return self._to_bars(rows)

    def get_result_status_bars(self) -> list[DashboardBar]:
        """Return enrolment result status distribution bars from approved data."""
        rows = db.session.execute(
            text(
                f"""
                SELECT result_status AS label, COUNT(*) AS value
                FROM {self.schema_name}.enrolment
                GROUP BY result_status
                ORDER BY value DESC, result_status
                """
            )
        ).mappings()
        return self._to_bars(rows)

    def _to_bars(self, rows) -> list[DashboardBar]:
        values = [(str(row["label"]), int(row["value"])) for row in rows]
        max_value = max((value for _, value in values), default=0)
        if max_value == 0:
            return []
        return [
            DashboardBar(
                label=label,
                value=value,
                percentage=max(4, round((value / max_value) * 100)),
            )
            for label, value in values
        ]
