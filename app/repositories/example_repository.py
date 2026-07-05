"""Repository for record persistence."""

from __future__ import annotations

from app.extensions import db
from app.models.example_model import Record


class RecordRepository:
    """Handle direct database access for records."""

    def create(self, *, name: str, description: str) -> Record:
        """Create and persist a new record."""
        record = Record(name=name, description=description)
        db.session.add(record)
        return record

    def list_all(self) -> list[Record]:
        """Return all records ordered by creation time."""
        return Record.query.order_by(Record.id.desc()).all()
