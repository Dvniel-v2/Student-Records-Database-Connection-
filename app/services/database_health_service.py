"""Service layer for database health checks."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError

from app.config import APPROVED_DATABASE_SCHEMA
from app.repositories.database_health_repository import DatabaseHealthRepository


@dataclass(frozen=True)
class DatabaseHealthResult:
    """Structured database health check result."""

    ok: bool
    connection: bool
    schema: bool
    student_table: bool
    message: str

    def to_dict(self) -> dict[str, bool | str]:
        """Return a JSON serialisable health result."""
        return {
            "ok": self.ok,
            "connection": self.connection,
            "schema": self.schema,
            "student_table": self.student_table,
            "message": self.message,
        }


class DatabaseHealthService:
    """Coordinate safe checks against the approved PostgreSQL schema."""

    def __init__(self, repository: DatabaseHealthRepository | None = None) -> None:
        self.repository = repository or DatabaseHealthRepository()

    def check(self) -> DatabaseHealthResult:
        """Check connection, schema availability and a core approved table."""
        try:
            connection = self.repository.connection_succeeds()
            schema = self.repository.schema_exists()
            student_table = False

            if schema:
                student_table = self.repository.student_table_queryable()

            ok = connection and schema and student_table
            message = (
                f"PostgreSQL schema '{APPROVED_DATABASE_SCHEMA}' is reachable."
                if ok
                else f"PostgreSQL schema '{APPROVED_DATABASE_SCHEMA}' is not ready."
            )
            return DatabaseHealthResult(
                ok=ok,
                connection=connection,
                schema=schema,
                student_table=student_table,
                message=message,
            )
        except SQLAlchemyError:
            return DatabaseHealthResult(
                ok=False,
                connection=False,
                schema=False,
                student_table=False,
                message="Database health check failed.",
            )
