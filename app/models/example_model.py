"""Example SQLAlchemy model."""

from __future__ import annotations

from app.extensions import db


class Record(db.Model):
    """Simple example record persisted to the database."""

    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self) -> dict[str, str | int]:
        """Return a dictionary representation for templates and tests."""
        return {"id": self.id, "name": self.name, "description": self.description}
