"""Read-only repository for approved academic record pages."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text

from app.config import APPROVED_DATABASE_SCHEMA
from app.extensions import db


class AcademicRecordRepository:
    """Read approved PostgreSQL records for non-Student pages."""

    def __init__(self, schema_name: str = APPROVED_DATABASE_SCHEMA) -> None:
        self.schema_name = schema_name

    def list_courses(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return approved course catalogue records."""
        rows = db.session.execute(
            text(
                f"""
                SELECT
                    c.course_code,
                    c.course_name,
                    d.department_code,
                    c.course_level,
                    c.credit_hours,
                    c.course_type,
                    COUNT(co.offering_id) AS offerings
                FROM {self.schema_name}.course c
                JOIN {self.schema_name}.department d
                    ON d.department_id = c.department_id
                LEFT JOIN {self.schema_name}.course_offering co
                    ON co.course_id = c.course_id
                GROUP BY
                    c.course_code,
                    c.course_name,
                    d.department_code,
                    c.course_level,
                    c.credit_hours,
                    c.course_type
                ORDER BY c.course_code
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings()
        return [dict(row) for row in rows]

    def list_modules(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return course offering records shown as teaching modules."""
        rows = db.session.execute(
            text(
                f"""
                SELECT
                    c.course_code,
                    c.course_name,
                    at.academic_year,
                    at.term_name,
                    co.section_code,
                    co.delivery_mode,
                    co.capacity,
                    co.status
                FROM {self.schema_name}.course_offering co
                JOIN {self.schema_name}.course c
                    ON c.course_id = co.course_id
                JOIN {self.schema_name}.academic_term at
                    ON at.term_id = co.term_id
                ORDER BY at.academic_year DESC, at.term_sequence, c.course_code
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings()
        return [dict(row) for row in rows]

    def list_enrolments(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return approved enrolment records."""
        rows = db.session.execute(
            text(
                f"""
                SELECT
                    s.student_number,
                    CONCAT(p.first_name, ' ', p.last_name) AS student_name,
                    c.course_code,
                    c.course_name,
                    at.term_name,
                    e.enrolment_status,
                    e.result_status,
                    e.enrolment_date
                FROM {self.schema_name}.enrolment e
                JOIN {self.schema_name}.student s
                    ON s.student_id = e.student_id
                JOIN {self.schema_name}.person p
                    ON p.person_id = s.person_id
                JOIN {self.schema_name}.course_offering co
                    ON co.offering_id = e.offering_id
                JOIN {self.schema_name}.course c
                    ON c.course_id = co.course_id
                JOIN {self.schema_name}.academic_term at
                    ON at.term_id = co.term_id
                ORDER BY e.enrolment_date DESC, s.student_number
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings()
        return [dict(row) for row in rows]

    def list_grades(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return approved grade records."""
        rows = db.session.execute(
            text(
                f"""
                SELECT
                    s.student_number,
                    CONCAT(p.first_name, ' ', p.last_name) AS student_name,
                    c.course_code,
                    g.assessment_type,
                    g.numeric_grade,
                    g.letter_grade,
                    g.recorded_at
                FROM {self.schema_name}.grade g
                JOIN {self.schema_name}.enrolment e
                    ON e.enrolment_id = g.enrolment_id
                JOIN {self.schema_name}.student s
                    ON s.student_id = e.student_id
                JOIN {self.schema_name}.person p
                    ON p.person_id = s.person_id
                JOIN {self.schema_name}.course_offering co
                    ON co.offering_id = e.offering_id
                JOIN {self.schema_name}.course c
                    ON c.course_id = co.course_id
                ORDER BY g.recorded_at DESC, s.student_number
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings()
        return [dict(row) for row in rows]

    def get_reports(self, limit: int = 20) -> dict[str, list[dict[str, Any]]]:
        """Return approved reporting view samples."""
        return {
            "course_enrolment": self._query_view(
                "vw_course_enrolment_summary",
                "academic_year DESC, term_name, course_code",
                limit,
            ),
            "programme_credit": self._query_view(
                "vw_programme_credit_summary",
                "programme_code",
                limit,
            ),
            "student_results": self._query_view(
                "vw_student_result_summary",
                "student_number",
                limit,
            ),
        }

    def _query_view(
        self, view_name: str, order_by: str, limit: int
    ) -> list[dict[str, Any]]:
        rows = db.session.execute(
            text(
                f"""
                SELECT *
                FROM {self.schema_name}.{view_name}
                ORDER BY {order_by}
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings()
        return [dict(row) for row in rows]
