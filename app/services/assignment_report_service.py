"""Service layer for assignment report query functions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.repositories.assignment_report_repository import AssignmentReportRepository


class AssignmentReportValidationError(ValueError):
    """Raised when report filters are invalid."""

    def __init__(self, errors: dict[str, str]) -> None:
        super().__init__("Report filters are invalid.")
        self.errors = errors


class AssignmentReportServiceError(RuntimeError):
    """Raised when report data cannot be read."""


@dataclass(frozen=True)
class ReportDefinition:
    """Metadata for an assignment report."""

    key: str
    name: str
    purpose: str
    required_filters: str
    columns: list[tuple[str, str]]


@dataclass(frozen=True)
class ReportResult:
    """Report page data."""

    definition: ReportDefinition
    rows: list[dict[str, Any]]
    filters: dict[str, str]
    choices: dict[str, list[dict[str, Any]]]
    errors: dict[str, str]
    has_run: bool


class AssignmentReportService:
    """Validate report filters and coordinate report queries."""

    DEFINITIONS: tuple[ReportDefinition, ...] = (
        ReportDefinition(
            "students-by-course-lecturer",
            "Students by Course and Lecturer",
            "Find Students registered on a selected course taught by a lecturer.",
            "Course and lecturer",
            [
                ("Student number", "student_number"),
                ("Student", "student_name"),
                ("Course", "course_code"),
                ("Course name", "course_name"),
                ("Lecturer", "lecturer_name"),
                ("Academic year", "academic_year"),
                ("Term", "term_name"),
                ("Section", "section_code"),
            ],
        ),
        ReportDefinition(
            "final-year-high-achievers",
            "Final-year Students Above 70%",
            "List final-year Students with an average overall grade above 70%.",
            "Minimum average grade",
            [
                ("Student number", "student_number"),
                ("Student", "student_name"),
                ("Programme", "programme_code"),
                ("Programme name", "programme_name"),
                ("Year", "year_of_study"),
                ("Average grade", "average_grade"),
            ],
        ),
        ReportDefinition(
            "students-without-current-registration",
            "Students Without Current Registration",
            "Find active Students without an enrolment in the current approved term.",
            "None",
            [
                ("Student number", "student_number"),
                ("Student", "student_name"),
                ("Programme", "programme_code"),
                ("Programme name", "programme_name"),
                ("Status", "student_status"),
                ("Academic year", "checked_academic_year"),
                ("Term", "checked_term"),
            ],
        ),
        ReportDefinition(
            "academic-adviser",
            "Academic Adviser Lookup",
            "Show current and recent adviser details for a selected Student.",
            "Student",
            [
                ("Student number", "student_number"),
                ("Student", "student_name"),
                ("Lecturer number", "lecturer_number"),
                ("Adviser", "adviser_name"),
                ("Masked email", "adviser_masked_email"),
                ("Department", "department_code"),
                ("Rank", "academic_rank"),
                ("Current", "is_current"),
            ],
        ),
        ReportDefinition(
            "lecturer-expertise",
            "Lecturers by Expertise",
            "Search lecturers by expertise area.",
            "Expertise search",
            [
                ("Lecturer number", "lecturer_number"),
                ("Lecturer", "lecturer_name"),
                ("Masked email", "masked_email"),
                ("Department", "department_code"),
                ("Department name", "department_name"),
                ("Expertise", "expertise_area"),
            ],
        ),
        ReportDefinition(
            "staff-by-location",
            "Staff by Department or Unit",
            "Find non-academic staff by department or administrative unit.",
            "Department or administrative unit",
            [
                ("Staff number", "staff_number"),
                ("Staff", "staff_name"),
                ("Masked email", "masked_email"),
                ("Role", "job_title"),
                ("Employment", "employment_type"),
                ("Location", "location_code"),
                ("Location name", "location_name"),
            ],
        ),
        ReportDefinition(
            "research-project-summary",
            "Research Project Summary",
            "Summarise research projects, funding, members, publications and outcomes.",
            "Optional project or group",
            [
                ("Project", "project_code"),
                ("Title", "project_title"),
                ("Group", "group_code"),
                ("Group name", "group_name"),
                ("Principal investigator", "principal_investigator"),
                ("Status", "project_status"),
                ("Funding", "funding_amount"),
                ("Members", "team_member_count"),
                ("Publications", "publication_count"),
                ("Outcomes", "outcome_count"),
            ],
        ),
        ReportDefinition(
            "programme-credit-summary",
            "Programme Credit Summary",
            "Compare required programme credits with approved curriculum credits.",
            "Optional programme",
            [
                ("Programme", "programme_code"),
                ("Programme name", "programme_name"),
                ("Degree", "degree_awarded"),
                ("Required credits", "required_credit_hours"),
                ("Course credits", "required_course_credit_hours"),
                ("Elective credits", "required_elective_credit_hours"),
                ("Curriculum credits", "curriculum_credit_hours"),
                ("Difference", "credit_difference"),
            ],
        ),
    )

    def __init__(self, repository: AssignmentReportRepository | None = None) -> None:
        self.repository = repository or AssignmentReportRepository()

    def catalogue(self) -> list[ReportDefinition]:
        """Return all supported assignment reports."""
        return list(self.DEFINITIONS)

    def get_definition(self, report_key: str) -> ReportDefinition:
        """Return report metadata by key."""
        for definition in self.DEFINITIONS:
            if definition.key == report_key:
                return definition
        raise AssignmentReportValidationError({"report": "Unknown report."})

    def build_report(
        self, report_key: str, filters: dict[str, str], *, has_run: bool
    ) -> ReportResult:
        """Return report page data and run the report when requested."""
        definition = self.get_definition(report_key)
        try:
            rows: list[dict[str, Any]] = []
            errors: dict[str, str] = {}
            cleaned = self._clean_filters(filters)
            choices = self._choices(report_key, cleaned)
            if has_run:
                try:
                    rows = self._run(report_key, cleaned)
                except AssignmentReportValidationError as exc:
                    errors = exc.errors
            return ReportResult(definition, rows, cleaned, choices, errors, has_run)
        except SQLAlchemyError as exc:
            raise AssignmentReportServiceError("Unable to read report data.") from exc

    def _choices(
        self, report_key: str, filters: dict[str, str]
    ) -> dict[str, list[dict[str, Any]]]:
        choices: dict[str, list[dict[str, Any]]] = {}
        if report_key == "students-by-course-lecturer":
            choices["lecturers"] = self.repository.list_lecturers()
            choices["courses"] = self.repository.list_lecturer_course_options()
        elif report_key == "academic-adviser":
            choices["students"] = self.repository.search_student_options(
                filters.get("student_search", ""),
                self._optional_int(filters.get("student_id", "")),
            )
        elif report_key == "lecturer-expertise":
            choices["expertise_areas"] = self.repository.list_expertise_areas()
        elif report_key == "staff-by-location":
            choices["locations"] = self.repository.list_staff_locations()
        elif report_key == "research-project-summary":
            choices["projects"] = self.repository.list_research_projects()
            choices["groups"] = self.repository.list_research_groups()
        elif report_key == "programme-credit-summary":
            choices["programmes"] = self.repository.list_programmes()
        return choices

    def _run(self, report_key: str, filters: dict[str, str]) -> list[dict[str, Any]]:
        if report_key == "students-by-course-lecturer":
            course_code = self._required(filters, "course_code", "Select a course.")
            lecturer_id = self._required_int(
                filters, "lecturer_id", "Select a lecturer."
            )
            return self.repository.students_by_course_and_lecturer(
                course_code, lecturer_id
            )
        if report_key == "final-year-high-achievers":
            minimum_grade = self._optional_float(filters, "minimum_grade", 70)
            return self.repository.final_year_average_above(minimum_grade)
        if report_key == "students-without-current-registration":
            return self.repository.students_without_current_registration()
        if report_key == "academic-adviser":
            student_id = self._required_int(filters, "student_id", "Select a Student.")
            return self.repository.adviser_for_student(student_id)
        if report_key == "lecturer-expertise":
            expertise = self._required(
                filters, "expertise_area", "Enter an expertise area."
            )
            return self.repository.lecturers_by_expertise(expertise)
        if report_key == "staff-by-location":
            location = self._required(filters, "location", "Select a location.")
            location_type, location_code = self._split_location(location)
            return self.repository.staff_by_location(location_type, location_code)
        if report_key == "research-project-summary":
            return self.repository.research_project_summary(
                filters.get("project_code", ""), filters.get("group_code", "")
            )
        if report_key == "programme-credit-summary":
            return self.repository.programme_credit_summary(
                filters.get("programme_code", "")
            )
        raise AssignmentReportValidationError({"report": "Unknown report."})

    def _clean_filters(self, filters: dict[str, str]) -> dict[str, str]:
        return {key: value.strip()[:120] for key, value in filters.items()}

    def _required(self, filters: dict[str, str], field: str, message: str) -> str:
        value = filters.get(field, "").strip()
        if not value:
            raise AssignmentReportValidationError({field: message})
        return value

    def _required_int(self, filters: dict[str, str], field: str, message: str) -> int:
        value = self._required(filters, field, message)
        try:
            return int(value)
        except ValueError as exc:
            raise AssignmentReportValidationError({field: message}) from exc

    def _optional_int(self, value: str) -> int | None:
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def _optional_float(
        self, filters: dict[str, str], field: str, default: float
    ) -> float:
        raw_value = filters.get(field, "").strip()
        if not raw_value:
            return default
        try:
            value = float(raw_value)
        except ValueError as exc:
            raise AssignmentReportValidationError(
                {field: "Enter a numeric grade threshold."}
            ) from exc
        if value < 0 or value > 100:
            raise AssignmentReportValidationError(
                {field: "Grade threshold must be between 0 and 100."}
            )
        return value

    def _split_location(self, location: str) -> tuple[str, str]:
        try:
            location_type, location_code = location.split(":", 1)
        except ValueError as exc:
            raise AssignmentReportValidationError(
                {"location": "Select a valid location."}
            ) from exc
        if location_type not in {"department", "unit"} or not location_code:
            raise AssignmentReportValidationError(
                {"location": "Select a valid location."}
            )
        return location_type, location_code
