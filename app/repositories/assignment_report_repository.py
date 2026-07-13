"""Repository for assignment report query functions."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import text

from app.config import APPROVED_DATABASE_SCHEMA
from app.extensions import db


class AssignmentReportRepository:
    """Run approved report queries against PostgreSQL."""

    def __init__(self, schema_name: str = APPROVED_DATABASE_SCHEMA) -> None:
        self.schema_name = schema_name

    def list_courses(self) -> list[dict[str, Any]]:
        """Return course filter options."""
        return self._rows(
            f"""
            SELECT course_code, course_name
            FROM {self.schema_name}.course
            ORDER BY course_code
            LIMIT 300
            """
        )

    def list_lecturers(self) -> list[dict[str, Any]]:
        """Return lecturer filter options."""
        return self._rows(
            f"""
            SELECT lecturer_id, lecturer_number,
                   CONCAT(first_name, ' ', last_name) AS lecturer_name,
                   department_code,
                   department_name
            FROM {self.schema_name}.vw_lecturer_directory_masked
            ORDER BY lecturer_name, lecturer_number
            LIMIT 300
            """
        )

    def list_expertise_areas(self) -> list[dict[str, Any]]:
        """Return lecturer expertise values for search suggestions."""
        return self._rows(
            f"""
            SELECT DISTINCT expertise_area
            FROM {self.schema_name}.lecturer_expertise
            ORDER BY expertise_area
            LIMIT 300
            """
        )

    def list_lecturer_course_options(self) -> list[dict[str, Any]]:
        """Return course options grouped by the lecturer teaching them."""
        return self._rows(
            f"""
            SELECT DISTINCT
                l.lecturer_id,
                c.course_code,
                c.course_name,
                COUNT(DISTINCT e.enrolment_id) AS enrolled_student_count
            FROM {self.schema_name}.offering_lecturer ol
            JOIN {self.schema_name}.lecturer l ON l.lecturer_id = ol.lecturer_id
            JOIN {self.schema_name}.course_offering co
                ON co.offering_id = ol.offering_id
            JOIN {self.schema_name}.course c ON c.course_id = co.course_id
            JOIN {self.schema_name}.enrolment e ON e.offering_id = co.offering_id
            GROUP BY l.lecturer_id, c.course_code, c.course_name
            HAVING COUNT(DISTINCT e.enrolment_id) > 0
            ORDER BY l.lecturer_id, c.course_code
            LIMIT 600
            """
        )

    def list_students(self) -> list[dict[str, Any]]:
        """Return student filter options."""
        return self._rows(
            f"""
            SELECT student_id, student_number,
                   CONCAT(first_name, ' ', last_name) AS student_name
            FROM {self.schema_name}.vw_student_directory_masked
            ORDER BY student_number
            LIMIT 300
            """
        )

    def search_student_options(
        self,
        search_term: str = "",
        selected_student_id: int | None = None,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Return a limited Student option list for report lookups."""
        where = []
        params: dict[str, Any] = {"limit": limit}
        if search_term:
            where.append(
                """
                (
                    student_number ILIKE :search_pattern
                    OR first_name ILIKE :search_pattern
                    OR last_name ILIKE :search_pattern
                    OR CONCAT(first_name, ' ', last_name) ILIKE :search_pattern
                    OR CONCAT(last_name, ' ', first_name) ILIKE :search_pattern
                )
                """
            )
            params["search_pattern"] = f"%{search_term}%"
        if selected_student_id is not None:
            where.append("student_id = :selected_student_id")
            params["selected_student_id"] = selected_student_id

        if not where:
            return []

        selected_order = (
            "CASE WHEN student_id = :selected_student_id THEN 0 ELSE 1 END,"
            if selected_student_id is not None
            else ""
        )

        return self._rows(
            f"""
            SELECT student_id, student_number,
                   CONCAT(first_name, ' ', last_name) AS student_name
            FROM {self.schema_name}.vw_student_directory_masked
            WHERE {' OR '.join(where)}
            ORDER BY {selected_order} student_number
            LIMIT :limit
            """,
            params,
        )

    def list_programmes(self) -> list[dict[str, Any]]:
        """Return programme filter options."""
        return self._rows(
            f"""
            SELECT programme_code, programme_name
            FROM {self.schema_name}.programme
            WHERE is_active IS TRUE
            ORDER BY programme_code
            """
        )

    def list_staff_locations(self) -> list[dict[str, Any]]:
        """Return department and administrative unit filter options."""
        return self._rows(
            f"""
            SELECT 'department' AS location_type,
                   department_code AS location_code,
                   department_name AS location_name
            FROM {self.schema_name}.department
            UNION ALL
            SELECT 'unit' AS location_type,
                   unit_code AS location_code,
                   unit_name AS location_name
            FROM {self.schema_name}.administrative_unit
            ORDER BY location_type, location_code
            """
        )

    def list_research_projects(self) -> list[dict[str, Any]]:
        """Return research project filter options."""
        return self._rows(
            f"""
            SELECT project_code, project_title
            FROM {self.schema_name}.research_project
            ORDER BY project_code
            LIMIT 300
            """
        )

    def list_research_groups(self) -> list[dict[str, Any]]:
        """Return research group filter options."""
        return self._rows(
            f"""
            SELECT group_code, group_name
            FROM {self.schema_name}.research_group
            ORDER BY group_code
            LIMIT 300
            """
        )

    def students_by_course_and_lecturer(
        self, course_code: str, lecturer_id: int
    ) -> list[dict[str, Any]]:
        """Return Students registered on a course taught by a lecturer."""
        return self._rows(
            f"""
            SELECT DISTINCT
                s.student_number,
                CONCAT(sp.first_name, ' ', sp.last_name) AS student_name,
                c.course_code,
                c.course_name,
                CONCAT(lp.first_name, ' ', lp.last_name) AS lecturer_name,
                at.academic_year,
                at.term_name,
                co.section_code
            FROM {self.schema_name}.enrolment e
            JOIN {self.schema_name}.student s ON s.student_id = e.student_id
            JOIN {self.schema_name}.person sp ON sp.person_id = s.person_id
            JOIN {self.schema_name}.course_offering co
                ON co.offering_id = e.offering_id
            JOIN {self.schema_name}.course c ON c.course_id = co.course_id
            JOIN {self.schema_name}.academic_term at ON at.term_id = co.term_id
            JOIN {self.schema_name}.offering_lecturer ol
                ON ol.offering_id = co.offering_id
            JOIN {self.schema_name}.lecturer l ON l.lecturer_id = ol.lecturer_id
            JOIN {self.schema_name}.person lp ON lp.person_id = l.person_id
            WHERE c.course_code = :course_code
              AND l.lecturer_id = :lecturer_id
            ORDER BY at.academic_year DESC, at.term_name, s.student_number
            LIMIT 500
            """,
            {"course_code": course_code, "lecturer_id": lecturer_id},
        )

    def final_year_average_above(self, minimum_grade: float) -> list[dict[str, Any]]:
        """Return final-year Students with average overall grade above threshold."""
        return self._rows(
            f"""
            SELECT
                s.student_number,
                CONCAT(p.first_name, ' ', p.last_name) AS student_name,
                pr.programme_code,
                pr.programme_name,
                s.year_of_study,
                ROUND(AVG(g.numeric_grade), 2) AS average_grade
            FROM {self.schema_name}.student s
            JOIN {self.schema_name}.person p ON p.person_id = s.person_id
            JOIN {self.schema_name}.programme pr ON pr.programme_id = s.programme_id
            JOIN {self.schema_name}.enrolment e ON e.student_id = s.student_id
            JOIN {self.schema_name}.grade g ON g.enrolment_id = e.enrolment_id
            WHERE s.year_of_study = pr.duration_years_max
              AND g.assessment_type = 'Overall'
            GROUP BY
                s.student_id,
                s.student_number,
                p.first_name,
                p.last_name,
                pr.programme_code,
                pr.programme_name,
                s.year_of_study
            HAVING AVG(g.numeric_grade) > :minimum_grade
            ORDER BY average_grade DESC, s.student_number
            LIMIT 500
            """,
            {"minimum_grade": minimum_grade},
        )

    def students_without_current_registration(self) -> list[dict[str, Any]]:
        """Return active Students without registration in the current approved term."""
        return self._rows(
            f"""
            WITH current_term AS (
                SELECT term_id, academic_year, term_name
                FROM {self.schema_name}.academic_term
                {self.current_term_order_sql()}
                LIMIT 1
            )
            SELECT
                s.student_number,
                CONCAT(p.first_name, ' ', p.last_name) AS student_name,
                pr.programme_code,
                pr.programme_name,
                s.student_status,
                ct.academic_year AS checked_academic_year,
                ct.term_name AS checked_term
            FROM {self.schema_name}.student s
            JOIN {self.schema_name}.person p ON p.person_id = s.person_id
            JOIN {self.schema_name}.programme pr ON pr.programme_id = s.programme_id
            CROSS JOIN current_term ct
            WHERE s.student_status = 'Active'
              AND NOT EXISTS (
                  SELECT 1
                  FROM {self.schema_name}.enrolment e
                  JOIN {self.schema_name}.course_offering co
                      ON co.offering_id = e.offering_id
                  WHERE e.student_id = s.student_id
                    AND co.term_id = ct.term_id
                    AND e.enrolment_status = 'Enrolled'
              )
            ORDER BY pr.programme_code, s.student_number
            LIMIT 500
            """
        )

    @staticmethod
    def current_term_order_sql() -> str:
        """Return the approved current-term fallback ordering."""
        return """
                ORDER BY
                    CASE
                        WHEN CURRENT_DATE BETWEEN start_date AND end_date THEN 0
                        WHEN start_date <= CURRENT_DATE THEN 1
                        ELSE 2
                    END,
                    CASE
                        WHEN start_date <= CURRENT_DATE THEN start_date
                    END DESC,
                    CASE
                        WHEN start_date > CURRENT_DATE THEN start_date
                    END ASC
        """

    @staticmethod
    def current_term_sort_key(
        start_date: date, end_date: date, today: date
    ) -> tuple[int, int]:
        """Mirror the SQL fallback order for unit tests and review."""
        if start_date <= today <= end_date:
            return (0, -start_date.toordinal())
        if start_date <= today:
            return (1, -start_date.toordinal())
        return (2, start_date.toordinal())

    def adviser_for_student(self, student_id: int) -> list[dict[str, Any]]:
        """Return current academic adviser details for a Student."""
        return self._rows(
            f"""
            SELECT
                s.student_number,
                CONCAT(sp.first_name, ' ', sp.last_name) AS student_name,
                l.lecturer_number,
                CONCAT(lp.first_name, ' ', lp.last_name) AS adviser_name,
                CONCAT(LEFT(lp.email, 2), '***@', split_part(lp.email, '@', 2))
                    AS adviser_masked_email,
                d.department_code,
                d.department_name,
                l.academic_rank,
                aa.start_date,
                aa.end_date,
                aa.is_current
            FROM {self.schema_name}.advisor_assignment aa
            JOIN {self.schema_name}.student s ON s.student_id = aa.student_id
            JOIN {self.schema_name}.person sp ON sp.person_id = s.person_id
            JOIN {self.schema_name}.lecturer l ON l.lecturer_id = aa.lecturer_id
            JOIN {self.schema_name}.person lp ON lp.person_id = l.person_id
            JOIN {self.schema_name}.department d ON d.department_id = l.department_id
            WHERE s.student_id = :student_id
            ORDER BY aa.is_current DESC, aa.start_date DESC
            LIMIT 20
            """,
            {"student_id": student_id},
        )

    def lecturers_by_expertise(self, expertise_area: str) -> list[dict[str, Any]]:
        """Return lecturers matching an expertise area."""
        return self._rows(
            f"""
            SELECT
                l.lecturer_number,
                CONCAT(p.first_name, ' ', p.last_name) AS lecturer_name,
                CONCAT(LEFT(p.email, 2), '***@', split_part(p.email, '@', 2))
                    AS masked_email,
                d.department_code,
                d.department_name,
                le.expertise_area
            FROM {self.schema_name}.lecturer_expertise le
            JOIN {self.schema_name}.lecturer l ON l.lecturer_id = le.lecturer_id
            JOIN {self.schema_name}.person p ON p.person_id = l.person_id
            JOIN {self.schema_name}.department d ON d.department_id = l.department_id
            WHERE le.expertise_area ILIKE :expertise_pattern
            ORDER BY d.department_code, lecturer_name, le.expertise_area
            LIMIT 500
            """,
            {"expertise_pattern": f"%{expertise_area}%"},
        )

    def staff_by_location(
        self, location_type: str, location_code: str
    ) -> list[dict[str, Any]]:
        """Return staff by department or administrative unit."""
        if location_type == "department":
            predicate = "d.department_code = :location_code"
        else:
            predicate = "au.unit_code = :location_code"
        return self._rows(
            f"""
            SELECT
                ns.staff_number,
                CONCAT(p.first_name, ' ', p.last_name) AS staff_name,
                CONCAT(LEFT(p.email, 2), '***@', split_part(p.email, '@', 2))
                    AS masked_email,
                ns.job_title,
                ns.employment_type,
                COALESCE(d.department_code, au.unit_code) AS location_code,
                COALESCE(d.department_name, au.unit_name) AS location_name
            FROM {self.schema_name}.non_academic_staff ns
            JOIN {self.schema_name}.person p ON p.person_id = ns.person_id
            LEFT JOIN {self.schema_name}.department d
                ON d.department_id = ns.department_id
            LEFT JOIN {self.schema_name}.administrative_unit au
                ON au.admin_unit_id = ns.admin_unit_id
            WHERE {predicate}
            ORDER BY ns.job_title, staff_name
            LIMIT 500
            """,
            {"location_code": location_code},
        )

    def research_project_summary(
        self, project_code: str = "", group_code: str = ""
    ) -> list[dict[str, Any]]:
        """Return research project summary rows."""
        where = []
        params: dict[str, Any] = {}
        if project_code:
            where.append("rp.project_code = :project_code")
            params["project_code"] = project_code
        if group_code:
            where.append("rg.group_code = :group_code")
            params["group_code"] = group_code
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        return self._rows(
            f"""
            WITH funding_totals AS (
                SELECT project_id, COALESCE(SUM(amount), 0) AS funding_amount
                FROM {self.schema_name}.project_funding
                GROUP BY project_id
            ),
            member_counts AS (
                SELECT project_id, COUNT(*) AS team_member_count
                FROM {self.schema_name}.research_project_member
                GROUP BY project_id
            ),
            publication_counts AS (
                SELECT project_id, COUNT(*) AS publication_count
                FROM {self.schema_name}.project_publication
                GROUP BY project_id
            ),
            outcome_counts AS (
                SELECT project_id, COUNT(*) AS outcome_count
                FROM {self.schema_name}.project_outcome
                GROUP BY project_id
            )
            SELECT
                rp.project_code,
                rp.project_title,
                rg.group_code,
                rg.group_name,
                CONCAT(pi_person.first_name, ' ', pi_person.last_name)
                    AS principal_investigator,
                rp.project_status,
                rp.start_date,
                rp.end_date,
                COALESCE(mc.team_member_count, 0) AS team_member_count,
                COALESCE(ft.funding_amount, 0) AS funding_amount,
                COALESCE(pc.publication_count, 0) AS publication_count,
                COALESCE(oc.outcome_count, 0) AS outcome_count
            FROM {self.schema_name}.research_project rp
            JOIN {self.schema_name}.research_group rg
                ON rg.research_group_id = rp.research_group_id
            JOIN {self.schema_name}.lecturer pi
                ON pi.lecturer_id = rp.principal_investigator_id
            JOIN {self.schema_name}.person pi_person
                ON pi_person.person_id = pi.person_id
            LEFT JOIN member_counts mc ON mc.project_id = rp.project_id
            LEFT JOIN funding_totals ft ON ft.project_id = rp.project_id
            LEFT JOIN publication_counts pc ON pc.project_id = rp.project_id
            LEFT JOIN outcome_counts oc ON oc.project_id = rp.project_id
            {where_sql}
            ORDER BY rp.project_status, rp.project_code
            LIMIT 500
            """,
            params,
        )

    def programme_credit_summary(
        self, programme_code: str = ""
    ) -> list[dict[str, Any]]:
        """Return programme credit summary rows."""
        where = "WHERE programme_code = :programme_code" if programme_code else ""
        params = {"programme_code": programme_code} if programme_code else {}
        return self._rows(
            f"""
            SELECT
                programme_code,
                programme_name,
                degree_awarded,
                required_credit_hours,
                required_course_credit_hours,
                required_elective_credit_hours,
                (
                    required_course_credit_hours + required_elective_credit_hours
                ) AS curriculum_credit_hours,
                (
                    required_credit_hours
                    - required_course_credit_hours
                    - required_elective_credit_hours
                ) AS credit_difference
            FROM {self.schema_name}.vw_programme_credit_summary
            {where}
            ORDER BY programme_code
            LIMIT 300
            """,
            params,
        )

    def _rows(
        self, sql: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        rows = db.session.execute(text(sql), params or {}).mappings()
        return [dict(row) for row in rows]
