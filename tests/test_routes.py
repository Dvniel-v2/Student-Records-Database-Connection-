"""Tests for the main routes."""

from app.repositories.approved_student_repository import ApprovedStudentRecord
from app.repositories.dashboard_repository import DashboardMetrics
from app.services.dashboard_service import DashboardData


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
        )


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


def test_create_student_is_not_yet_available_for_normalised_schema(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "student_service", FakeApprovedStudentService())

    response = client.post("/students", data={}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Student record creation is not yet available" in response.data


def test_edit_student_is_not_yet_available_for_normalised_schema(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "student_service", FakeApprovedStudentService())

    response = client.post("/students/1/edit", data={}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Student editing is not yet available" in response.data


def test_delete_student_is_not_yet_available_for_normalised_schema(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "student_service", FakeApprovedStudentService())

    response = client.post("/students/1/delete", follow_redirects=True)

    assert response.status_code == 200
    assert b"Student deletion is not yet available" in response.data
