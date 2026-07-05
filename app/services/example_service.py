"""Service layer for record management."""

from __future__ import annotations

from app.extensions import db
from app.models.example_model import Record
from app.repositories.example_repository import RecordRepository


class RecordService:
    """Encapsulate business logic and validation for records."""

    def __init__(self, repository: RecordRepository | None = None) -> None:
        self.repository = repository or RecordRepository()

    def create_record(self, *, name: str, description: str) -> Record:
        """Validate and persist a new record."""
        cleaned_name = name.strip()
        cleaned_description = description.strip()

        if not cleaned_name:
            raise ValueError("Name is required.")
        if len(cleaned_name) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        if not cleaned_description:
            raise ValueError("Description is required.")

        try:
            record = self.repository.create(
                name=cleaned_name,
                description=cleaned_description,
            )
            db.session.commit()
            return record
        except Exception as exc:  # pragma: no cover - defensive error handling
            db.session.rollback()
            raise RuntimeError(f"Unable to save record: {exc}") from exc

    def list_records(self) -> list[Record]:
        """Return all persisted records."""
        return self.repository.list_all()
