"""Tests for approved student repository query construction."""

from app.repositories.approved_student_repository import ApprovedStudentRepository


class FakeScalarResult:
    """Fake scalar result for repository count queries."""

    def scalar_one(self):
        return 0


class FakeMappingRows:
    """Fake row mapping result for repository list queries."""

    def mappings(self):
        return []


class FakeSession:
    """Capture SQL sent through the repository."""

    def __init__(self):
        self.statements = []

    def execute(self, statement, params=None):
        self.statements.append((str(statement), params or {}))
        if "COUNT(*)" in str(statement):
            return FakeScalarResult()
        return FakeMappingRows()


def test_student_search_matches_concatenated_full_name(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(
        "app.repositories.approved_student_repository.db.session", session
    )
    repository = ApprovedStudentRepository("use_record_management")

    repository.search_students(search_term="Ada Lovelace")

    search_sql = " ".join(statement for statement, _params in session.statements)
    assert "CONCAT(first_name, ' ', last_name) ILIKE :search_pattern" in search_sql
    assert "CONCAT(last_name, ' ', first_name) ILIKE :search_pattern" in search_sql
    assert session.statements[0][1]["search_pattern"] == "%Ada Lovelace%"
