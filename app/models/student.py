"""Legacy simplified Student SQLAlchemy model.

The approved PostgreSQL implementation uses the normalised
use_record_management.person, student and programme tables. Keep this model only
until the legacy prototype write path is fully replaced.
"""

from __future__ import annotations

from datetime import date

from app.extensions import db


class Student(db.Model):
    """Legacy student record persisted to the simplified prototype table."""

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(20), nullable=False, unique=True, index=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    course = db.Column(db.String(120), nullable=False)
    enrolment_date = db.Column(db.Date, nullable=False)

    def to_dict(self) -> dict[str, str | int]:
        """Return a dictionary representation for templates and tests."""
        return {
            "id": self.id,
            "student_number": self.student_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "course": self.course,
            "enrolment_date": (
                self.enrolment_date.isoformat()
                if isinstance(self.enrolment_date, date)
                else self.enrolment_date
            ),
        }
