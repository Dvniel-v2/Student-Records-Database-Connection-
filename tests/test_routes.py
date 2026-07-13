"""Tests for the main routes."""

import re

from app.repositories.approved_student_repository import ApprovedStudentRecord
from app.repositories.dashboard_repository import DashboardBar, DashboardMetrics
from app.repositories.student_write_repository import EditableStudentRecord
from app.services.academic_record_service import RecordPage
from app.services.assignment_report_service import (
    AssignmentReportService,
    AssignmentReportServiceError,
)
from app.services.dashboard_service import DashboardData
from app.services.student_write_service import (
    StudentFormChoices,
    StudentWriteConflictError,
    StudentWriteServiceError,
    StudentWriteValidationError,
)


def _approved_student() -> ApprovedStudentRecord:
    return ApprovedStudentRecord(
        student_id=1,
        student_number="USE1001",
        first_name="Ada",
        last_name="Lovelace",
        masked_email="ad***@use.edu",
        programme_code="UB-CSC",
        programme_name="B.Sc. Computer Science",
        enrolment_year=2024,
        year_of_study=1,
        student_status="Active",
        graduation_status="Not eligible",
    )


class FakeApprovedStudentService:
    """Fake approved service for route tests."""

    PER_PAGE_OPTIONS = (25, 50, 100)

    def list_students(self):
        return [_approved_student()]

    def search_students(self, **kwargs):
        self.last_search = kwargs

        class Result:
            students = [_approved_student()]
            total_records = 1
            page = 1
            per_page = kwargs.get("per_page", 25)
            total_pages = 1

        return Result()

    def get_student(self, student_id: int):
        if student_id == 1:
            return _approved_student()
        return None

    def list_programmes(self):
        return []

    def list_statuses(self):
        return ["Active"]

    def get_status_summary(self):
        class Summary:
            total = 1
            by_status = {"Active": 1}

        return Summary()


class FakeDashboardService:
    """Fake dashboard service for route tests."""

    def get_dashboard(self):
        return DashboardData(
            metrics=DashboardMetrics(
                total_students=1,
                active_programmes=1,
                current_enrolments=1,
                results_in_progress=1,
            ),
            students=[_approved_student()],
            student_status_bars=[DashboardBar("Active", 1, 100)],
            result_status_bars=[DashboardBar("In progress", 1, 100)],
        )


class FakeAcademicRecordService:
    """Fake academic service for read-only record route tests."""

    def _page(self, title: str) -> RecordPage:
        return RecordPage(
            title=title,
            subtitle=f"Approved {title.lower()}",
            description=f"Read-only {title.lower()} from approved PostgreSQL records.",
            columns=[("Code", "code"), ("Name", "name")],
            rows=[{"code": "USE101", "name": f"{title} sample"}],
        )

    def courses_page(self) -> RecordPage:
        return self._page("Courses")

    def modules_page(self) -> RecordPage:
        return self._page("Modules")

    def enrolments_page(self) -> RecordPage:
        return self._page("Enrolments")

    def grades_page(self) -> RecordPage:
        return self._page("Grades")

    def reports(self):
        return {
            "course_enrolment": [{"course_code": "USE101", "enrolled_students": 12}],
            "programme_credit": [{"programme_code": "UB-CSC", "total_credits": 360}],
            "student_results": [{"student_number": "USE1001", "average_grade": 72}],
        }


class FakeAssignmentReportService:
    """Fake report service for route tests."""

    def __init__(self):
        self.error = None

    def catalogue(self):
        return AssignmentReportService.DEFINITIONS[:2]

    def build_report(self, report_key, filters, *, has_run):
        if self.error:
            raise self.error

        definition = AssignmentReportService().get_definition(report_key)

        class Result:
            rows = [{"student_number": "USE1001", "student_name": "Ada Lovelace"}]
            choices = {
                "students": [
                    {
                        "student_id": 1,
                        "student_number": "USE1001",
                        "student_name": "Ada Lovelace",
                    }
                ]
            }
            errors = {}

        result = Result()
        result.definition = definition
        result.filters = filters
        result.has_run = has_run
        return result


def _editable_student() -> EditableStudentRecord:
    return EditableStudentRecord(
        student_id=1,
        person_id=10,
        student_number="USE1001",
        first_name="Ada",
        last_name="Lovelace",
        masked_email="ad***@use.edu",
        phone="+44 100",
        nationality="British",
        programme_code="UB-CSC",
        programme_name="B.Sc. Computer Science",
        date_of_birth="2001-01-01",
        enrolment_year=2024,
        year_of_study=1,
        admission_type="Local",
        student_status="Active",
        graduation_status="Not eligible",
    )


class FakeStudentWriteService:
    """Fake write service for Student CRUD route tests."""

    def __init__(self):
        self.created_form = None
        self.updated_form = None
        self.withdrawn_id = None
        self.create_error = None
        self.update_error = None
        self.withdraw_error = None

    def form_choices(self):
        return StudentFormChoices(
            programmes=[
                type(
                    "Programme",
                    (),
                    {
                        "programme_code": "UB-CSC",
                        "programme_name": "B.Sc. Computer Science",
                    },
                )()
            ]
        )

    def get_student_for_edit(self, student_id: int):
        if student_id == 1:
            return _editable_student()
        return None

    def create_student(self, form):
        self.created_form = form
        if self.create_error:
            raise self.create_error
        return 1

    def update_student(self, student_id: int, form):
        self.updated_form = form
        if self.update_error:
            raise self.update_error

    def withdraw_student(self, student_id: int):
        self.withdrawn_id = student_id
        if self.withdraw_error:
            raise self.withdraw_error


def _csrf_token(response) -> str:
    match = re.search(
        r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True)
    )
    assert match is not None
    return match.group(1)


def test_dashboard_page_renders_metrics_and_overview(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "dashboard_service", FakeDashboardService())

    response = client.get("/")

    assert response.status_code == 200
    assert b"UniRecords" in response.data
    assert b"University Records Dashboard" in response.data
    assert b"USE1001" in response.data


def test_students_page_renders_searchable_directory(client, monkeypatch):
    from app.routes import main

    fake_service = FakeApprovedStudentService()
    monkeypatch.setattr(main, "student_service", fake_service)

    response = client.get("/students?q=Ada&status=Active&per_page=50")

    assert response.status_code == 200
    assert b"Student Records" in response.data
    assert b"USE1001" in response.data
    assert fake_service.last_search["search_term"] == "Ada"
    assert fake_service.last_search["status"] == "Active"
    assert fake_service.last_search["per_page"] == 50


def test_view_student_renders_approved_detail(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "student_service", FakeApprovedStudentService())

    response = client.get("/students/1")

    assert response.status_code == 200
    assert b"Ada Lovelace" in response.data
    assert b"ad***@use.edu" in response.data
    assert b"UB-CSC" in response.data


def test_view_missing_student_redirects(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "student_service", FakeApprovedStudentService())

    response = client.get("/students/999", follow_redirects=True)

    assert response.status_code == 200
    assert b"Student not found." in response.data


def test_create_student_form_loads_reference_data(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "student_write_service", FakeStudentWriteService())

    response = client.get("/students/new")

    assert response.status_code == 200
    assert b"Add Student" in response.data
    assert b"UB-CSC" in response.data


def test_create_valid_student_redirects_to_detail(client, monkeypatch):
    from app.routes import main

    fake_service = FakeStudentWriteService()
    monkeypatch.setattr(main, "student_write_service", fake_service)
    form_response = client.get("/students/new")
    token = _csrf_token(form_response)

    response = client.post(
        "/students",
        data={
            "csrf_token": token,
            "student_number": "use1001",
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@stu.use.edu",
            "programme_code": "UB-CSC",
            "date_of_birth": "2001-01-01",
            "enrolment_year": "2024",
            "year_of_study": "1",
            "admission_type": "Local",
            "student_status": "Active",
            "graduation_status": "Not eligible",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/students/1")
    assert fake_service.created_form["first_name"] == "Ada"


def test_create_invalid_student_shows_field_errors(client, monkeypatch):
    from app.routes import main

    fake_service = FakeStudentWriteService()
    fake_service.create_error = StudentWriteValidationError(
        {"email": "Enter a valid email address."}
    )
    monkeypatch.setattr(main, "student_write_service", fake_service)
    token = _csrf_token(client.get("/students/new"))

    response = client.post(
        "/students",
        data={"csrf_token": token, "email": "bad"},
    )

    assert response.status_code == 400
    assert b"Enter a valid email address." in response.data


def test_create_duplicate_student_shows_conflict(client, monkeypatch):
    from app.routes import main

    fake_service = FakeStudentWriteService()
    fake_service.create_error = StudentWriteConflictError(
        "A Student with this number already exists."
    )
    monkeypatch.setattr(main, "student_write_service", fake_service)
    token = _csrf_token(client.get("/students/new"))

    response = client.post(
        "/students",
        data={"csrf_token": token, "student_number": "USE1001"},
    )

    assert response.status_code == 409
    assert b"A Student with this number already exists." in response.data


def test_edit_student_form_loads_existing_data(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "student_write_service", FakeStudentWriteService())

    response = client.get("/students/1/edit")

    assert response.status_code == 200
    assert b"Edit Student" in response.data
    assert b"USE1001" in response.data


def test_update_valid_student_redirects_to_detail(client, monkeypatch):
    from app.routes import main

    fake_service = FakeStudentWriteService()
    monkeypatch.setattr(main, "student_write_service", fake_service)
    token = _csrf_token(client.get("/students/1/edit"))

    response = client.post(
        "/students/1/edit",
        data={
            "csrf_token": token,
            "student_number": "USE1001",
            "first_name": "Ada",
            "last_name": "Lovelace",
            "programme_code": "UB-CSC",
            "date_of_birth": "2001-01-01",
            "enrolment_year": "2024",
            "year_of_study": "2",
            "admission_type": "Local",
            "student_status": "Active",
            "graduation_status": "Not eligible",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/students/1")
    assert fake_service.updated_form["year_of_study"] == "2"


def test_update_invalid_student_shows_errors(client, monkeypatch):
    from app.routes import main

    fake_service = FakeStudentWriteService()
    fake_service.update_error = StudentWriteValidationError(
        {"year_of_study": "Year of study must be between 1 and 8."}
    )
    monkeypatch.setattr(main, "student_write_service", fake_service)
    token = _csrf_token(client.get("/students/1/edit"))

    response = client.post(
        "/students/1/edit",
        data={"csrf_token": token, "year_of_study": "99"},
    )

    assert response.status_code == 400
    assert b"Year of study must be between 1 and 8." in response.data


def test_withdraw_student_confirmation_loads(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "student_service", FakeApprovedStudentService())

    response = client.get("/students/1/delete")

    assert response.status_code == 200
    assert b"Withdraw Student" in response.data
    assert b"USE1001" in response.data


def test_successful_withdraw_student(client, monkeypatch):
    from app.routes import main

    fake_write_service = FakeStudentWriteService()
    monkeypatch.setattr(main, "student_service", FakeApprovedStudentService())
    monkeypatch.setattr(main, "student_write_service", fake_write_service)
    token = _csrf_token(client.get("/students/1/delete"))

    response = client.post("/students/1/delete", data={"csrf_token": token})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/students/1")
    assert fake_write_service.withdrawn_id == 1


def test_blocked_withdraw_student_shows_safe_message(client, monkeypatch):
    from app.routes import main

    fake_write_service = FakeStudentWriteService()
    fake_write_service.withdraw_error = StudentWriteServiceError(
        "Database failure should not be displayed."
    )
    monkeypatch.setattr(main, "student_write_service", fake_write_service)

    with client.session_transaction() as session:
        session["_csrf_token"] = "known-token"

    response = client.post(
        "/students/1/delete",
        data={"csrf_token": "known-token"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Student could not be withdrawn." in response.data


def test_student_post_requires_csrf_token(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "student_write_service", FakeStudentWriteService())

    response = client.post("/students", data={})

    assert response.status_code == 400


def test_academic_record_pages_render_read_only_data(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "academic_service", FakeAcademicRecordService())

    for path, expected in [
        ("/courses", b"Courses sample"),
        ("/modules", b"Modules sample"),
        ("/enrolments", b"Enrolments sample"),
        ("/grades", b"Grades sample"),
    ]:
        response = client.get(path)

        assert response.status_code == 200
        assert b"Read only" in response.data
        assert expected in response.data


def test_reports_page_renders_approved_report_sections(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(
        main, "assignment_report_service", FakeAssignmentReportService()
    )

    response = client.get("/reports")

    assert response.status_code == 200
    assert b"Students by Course and Lecturer" in response.data
    assert b"Open Filters" in response.data


def test_report_detail_runs_with_filters(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(
        main, "assignment_report_service", FakeAssignmentReportService()
    )

    response = client.get("/reports/academic-adviser?run=1&student_id=1")

    assert response.status_code == 200
    assert b"Academic Adviser Lookup" in response.data
    assert b"USE1001" in response.data


def test_report_detail_handles_service_error(client, monkeypatch):
    from app.routes import main

    fake_service = FakeAssignmentReportService()
    fake_service.error = AssignmentReportServiceError("database unavailable")
    monkeypatch.setattr(main, "assignment_report_service", fake_service)

    response = client.get(
        "/reports/academic-adviser?run=1&student_id=1", follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Report data is currently unavailable." in response.data
