"""Repository checks for the approved PostgreSQL database."""

from __future__ import annotations

from sqlalchemy import text

from app.config import APPROVED_DATABASE_SCHEMA
from app.extensions import db


class DatabaseHealthRepository:
    """Run direct database checks without exposing connection details."""

    def __init__(self, schema_name: str = APPROVED_DATABASE_SCHEMA) -> None:
        self.schema_name = schema_name

    def connection_succeeds(self) -> bool:
        """Return whether SQLAlchemy can execute a basic statement."""
        db.session.execute(text("SELECT 1")).scalar_one()
        return True

    def schema_exists(self) -> bool:
        """Return whether the approved PostgreSQL schema exists."""
        result = db.session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.schemata
                    WHERE schema_name = :schema_name
                )
                """
            ),
            {"schema_name": self.schema_name},
        ).scalar_one()
        return bool(result)

    def student_table_queryable(self) -> bool:
        """Return whether the approved student table can be queried."""
        db.session.execute(
            text(f"SELECT 1 FROM {self.schema_name}.student LIMIT 1")
        ).first()
        return True
