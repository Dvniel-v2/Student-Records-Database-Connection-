"""Tests for the main routes."""

from app.repositories.approved_student_repository import ApprovedStudentRecord


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

    def list_students(self):
        return [_approved_student()]

    def get_student(self, student_id: int):
        if student_id == 1:
            return _approved_student()
        return None


def test_index_page_renders_approved_students(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "service", FakeApprovedStudentService())

    response = client.get("/")

    assert response.status_code == 200
    assert b"UniRecords" in response.data
    assert b"Student Records" in response.data
    assert b"USE1001" in response.data
    assert b"B.Sc. Computer Science" in response.data


def test_view_student_renders_approved_detail(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "service", FakeApprovedStudentService())

    response = client.get("/students/1")

    assert response.status_code == 200
    assert b"Ada Lovelace" in response.data
    assert b"ad***@use.edu" in response.data
    assert b"UB-CSC" in response.data


def test_view_missing_student_redirects(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "service", FakeApprovedStudentService())

    response = client.get("/students/999", follow_redirects=True)

    assert response.status_code == 200
    assert b"Student not found." in response.data


def test_create_student_is_disabled_during_postgresql_migration(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "service", FakeApprovedStudentService())

    response = client.post("/students", data={}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Student record creation is disabled during PostgreSQL migration." in (
        response.data
    )


def test_edit_student_is_disabled_during_postgresql_migration(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "service", FakeApprovedStudentService())

    response = client.post("/students/1/edit", data={}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Student editing is disabled during PostgreSQL migration." in response.data


def test_delete_student_is_disabled_during_postgresql_migration(client, monkeypatch):
    from app.routes import main

    monkeypatch.setattr(main, "service", FakeApprovedStudentService())

    response = client.post("/students/1/delete", follow_redirects=True)

    assert response.status_code == 200
    assert b"Student deletion is disabled during PostgreSQL migration." in response.data
