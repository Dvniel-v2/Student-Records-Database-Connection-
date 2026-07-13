"""Tests for assignment report service validation."""

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.services.assignment_report_service import (
    AssignmentReportService,
    AssignmentReportServiceError,
)


class FakeReportRepository:
    """Repository fake for assignment report service tests."""

    def __init__(self):
        self.raise_error = False

    def list_courses(self):
        if self.raise_error:
            raise SQLAlchemyError("database down")
        return [{"course_code": "UCSC101", "course_name": "Databases"}]

    def list_lecturers(self):
        if self.raise_error:
            raise SQLAlchemyError("database down")
        return [
            {
                "lecturer_id": 1,
                "lecturer_number": "L1",
                "lecturer_name": "Dr Ada",
                "department_code": "CSC",
            }
        ]

    def list_expertise_areas(self):
        return [{"expertise_area": "Databases"}]

    def list_lecturer_course_options(self):
        if self.raise_error:
            raise SQLAlchemyError("database down")
        return [
            {
                "lecturer_id": 1,
                "course_code": "UCSC101",
                "course_name": "Databases",
                "enrolled_student_count": 12,
            }
        ]

    def list_students(self):
        return [{"student_id": 1, "student_number": "S1", "student_name": "Ada"}]

    def list_programmes(self):
        return [{"programme_code": "UB-CSC", "programme_name": "Computer Science"}]

    def list_staff_locations(self):
        return [
            {
                "location_type": "department",
                "location_code": "CSC",
                "location_name": "Computer Science",
            }
        ]

    def list_research_projects(self):
        return [{"project_code": "RP1", "project_title": "Research"}]

    def list_research_groups(self):
        return [{"group_code": "RG1", "group_name": "Group"}]

    def students_by_course_and_lecturer(self, course_code, lecturer_id):
        return [{"student_number": "S1", "lecturer_id": lecturer_id}]

    def final_year_average_above(self, minimum_grade):
        return [{"student_number": "S1", "average_grade": minimum_grade + 1}]

    def students_without_current_registration(self):
        return [{"student_number": "S1"}]

    def adviser_for_student(self, student_id):
        return [{"student_number": "S1", "student_id": student_id}]

    def lecturers_by_expertise(self, expertise_area):
        return [{"lecturer_name": "Dr Ada", "expertise_area": expertise_area}]

    def staff_by_location(self, location_type, location_code):
        return [{"staff_name": "Admin", "location_code": location_code}]

    def research_project_summary(self, project_code="", group_code=""):
        return [{"project_code": project_code or "RP1"}]

    def programme_credit_summary(self, programme_code=""):
        return [{"programme_code": programme_code or "UB-CSC"}]


def test_catalogue_contains_all_assignment_reports():
    service = AssignmentReportService(FakeReportRepository())

    assert len(service.catalogue()) == 8


def test_report_requires_course_and_lecturer_filters():
    service = AssignmentReportService(FakeReportRepository())

    report = service.build_report(
        "students-by-course-lecturer", {"course_code": ""}, has_run=True
    )

    assert "course_code" in report.errors


def test_report_runs_valid_course_and_lecturer_filters():
    service = AssignmentReportService(FakeReportRepository())

    report = service.build_report(
        "students-by-course-lecturer",
        {"course_code": "UCSC101", "lecturer_id": "1"},
        has_run=True,
    )

    assert report.rows[0]["student_number"] == "S1"


def test_invalid_numeric_filter_returns_field_error():
    service = AssignmentReportService(FakeReportRepository())

    report = service.build_report(
        "final-year-high-achievers", {"minimum_grade": "high"}, has_run=True
    )

    assert "minimum_grade" in report.errors


def test_lecturer_expertise_report_includes_search_suggestions():
    service = AssignmentReportService(FakeReportRepository())

    report = service.build_report("lecturer-expertise", {}, has_run=False)

    assert report.choices["expertise_areas"][0]["expertise_area"] == "Databases"


def test_repository_error_becomes_service_error():
    repository = FakeReportRepository()
    repository.raise_error = True
    service = AssignmentReportService(repository)

    with pytest.raises(AssignmentReportServiceError):
        service.build_report("students-by-course-lecturer", {}, has_run=False)
