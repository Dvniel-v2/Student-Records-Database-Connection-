"""Tests for assignment report repository query construction."""

from datetime import date

from app.repositories.assignment_report_repository import AssignmentReportRepository


class FakeMappingRows:
    """Fake SQLAlchemy mapping result."""

    def mappings(self):
        return []


class FakeSession:
    """Capture repository SQL statements."""

    def __init__(self):
        self.statements = []

    def execute(self, statement, params=None):
        self.statements.append((str(statement), params or {}))
        return FakeMappingRows()


def test_research_summary_aggregates_independent_child_tables(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(
        "app.repositories.assignment_report_repository.db.session", session
    )
    repository = AssignmentReportRepository("use_record_management")

    repository.research_project_summary(project_code="RP1", group_code="RG1")

    sql = session.statements[0][0]
    params = session.statements[0][1]
    assert "WITH funding_totals AS" in sql
    assert "SUM(amount)" in sql
    assert "SUM(DISTINCT pf.amount)" not in sql
    assert "member_counts AS" in sql
    assert "publication_counts AS" in sql
    assert "outcome_counts AS" in sql
    assert params == {"project_code": "RP1", "group_code": "RG1"}


def test_current_term_order_prefers_active_then_historical_then_future():
    order_sql = AssignmentReportRepository.current_term_order_sql()

    assert "CURRENT_DATE BETWEEN start_date AND end_date THEN 0" in order_sql
    assert "WHEN start_date <= CURRENT_DATE THEN 1" in order_sql
    assert "ELSE 2" in order_sql
    assert "END DESC" in order_sql
    assert "END ASC" in order_sql


def test_current_term_sort_prefers_active_current_term():
    today = date(2026, 7, 13)
    terms = [
        ("future", date(2026, 9, 1), date(2026, 12, 15)),
        ("active", date(2026, 6, 1), date(2026, 8, 15)),
        ("historical", date(2026, 1, 1), date(2026, 5, 31)),
    ]

    selected = min(
        terms,
        key=lambda term: AssignmentReportRepository.current_term_sort_key(
            term[1], term[2], today
        ),
    )

    assert selected[0] == "active"


def test_current_term_sort_uses_recent_historical_term_between_terms():
    today = date(2026, 8, 20)
    terms = [
        ("old", date(2026, 1, 1), date(2026, 5, 31)),
        ("recent", date(2026, 6, 1), date(2026, 8, 15)),
        ("future", date(2026, 9, 1), date(2026, 12, 15)),
    ]

    selected = min(
        terms,
        key=lambda term: AssignmentReportRepository.current_term_sort_key(
            term[1], term[2], today
        ),
    )

    assert selected[0] == "recent"


def test_current_term_sort_uses_future_term_only_when_no_history_exists():
    today = date(2026, 1, 1)
    terms = [
        ("later", date(2026, 9, 1), date(2026, 12, 15)),
        ("next", date(2026, 2, 1), date(2026, 5, 31)),
    ]

    selected = min(
        terms,
        key=lambda term: AssignmentReportRepository.current_term_sort_key(
            term[1], term[2], today
        ),
    )

    assert selected[0] == "next"


def test_current_term_sort_uses_latest_of_multiple_historical_terms():
    today = date(2027, 1, 1)
    terms = [
        ("old", date(2026, 1, 1), date(2026, 5, 31)),
        ("latest", date(2026, 9, 1), date(2026, 12, 15)),
        ("middle", date(2026, 6, 1), date(2026, 8, 15)),
    ]

    selected = min(
        terms,
        key=lambda term: AssignmentReportRepository.current_term_sort_key(
            term[1], term[2], today
        ),
    )

    assert selected[0] == "latest"


def test_students_without_current_registration_uses_term_fallback(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(
        "app.repositories.assignment_report_repository.db.session", session
    )
    repository = AssignmentReportRepository("use_record_management")

    repository.students_without_current_registration()

    sql = session.statements[0][0]
    assert "WITH current_term AS" in sql
    assert "CURRENT_DATE BETWEEN start_date AND end_date THEN 0" in sql
    assert "WHEN start_date <= CURRENT_DATE THEN 1" in sql
    assert "ELSE 2" in sql
    assert "ct.academic_year AS checked_academic_year" in sql
    assert "ct.term_name AS checked_term" in sql


def test_adviser_student_lookup_searches_full_names_and_limits_results(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(
        "app.repositories.assignment_report_repository.db.session", session
    )
    repository = AssignmentReportRepository("use_record_management")

    repository.search_student_options("Ada Lovelace", selected_student_id=10)

    sql = session.statements[0][0]
    params = session.statements[0][1]
    assert "student_number ILIKE :search_pattern" in sql
    assert "CONCAT(first_name, ' ', last_name) ILIKE :search_pattern" in sql
    assert "CONCAT(last_name, ' ', first_name) ILIKE :search_pattern" in sql
    assert "student_id = :selected_student_id" in sql
    assert "CASE WHEN student_id = :selected_student_id THEN 0 ELSE 1 END" in sql
    assert "LIMIT :limit" in sql
    assert params["search_pattern"] == "%Ada Lovelace%"
    assert params["selected_student_id"] == 10
    assert params["limit"] == 25


def test_adviser_student_lookup_returns_empty_without_search_or_selection():
    repository = AssignmentReportRepository("use_record_management")

    assert repository.search_student_options() == []
