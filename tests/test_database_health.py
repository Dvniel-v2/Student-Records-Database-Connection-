"""Tests for database health-check behaviour."""

from app.services.database_health_service import DatabaseHealthService


class HealthyRepository:
    """Fake repository for a reachable approved database."""

    def connection_succeeds(self) -> bool:
        return True

    def schema_exists(self) -> bool:
        return True

    def student_table_queryable(self) -> bool:
        return True


class MissingSchemaRepository(HealthyRepository):
    """Fake repository for a database without the approved schema."""

    def schema_exists(self) -> bool:
        return False


def test_database_health_passes_when_schema_and_student_table_are_ready():
    result = DatabaseHealthService(HealthyRepository()).check()

    assert result.ok is True
    assert result.connection is True
    assert result.schema is True
    assert result.student_table is True


def test_database_health_fails_when_schema_is_missing():
    result = DatabaseHealthService(MissingSchemaRepository()).check()

    assert result.ok is False
    assert result.connection is True
    assert result.schema is False
    assert result.student_table is False


def test_database_health_route_reports_unavailable_for_sqlite(client):
    response = client.get("/health/database")

    assert response.status_code == 503
    assert response.get_json()["ok"] is False
