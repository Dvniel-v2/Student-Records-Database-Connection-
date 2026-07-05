"""Student SQLAlchemy model."""

from __future__ import annotations

from datetime import date

from app.extensions import db


class Student(db.Model):
    """Student record persisted to the database."""

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
