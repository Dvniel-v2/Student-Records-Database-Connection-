"""Legacy repository for simplified student persistence.

The approved read-only Student path uses ApprovedStudentRepository against the
normalised PostgreSQL schema. Keep this repository only until legacy writes are
removed.
"""

from __future__ import annotations

from datetime import date

from app.extensions import db
from app.models.student import Student


class StudentRepository:
    """Handle direct database access for legacy simplified students."""

    def create(
        self,
        *,
        student_number: str,
        first_name: str,
        last_name: str,
        email: str,
        course: str,
        enrolment_date: date,
    ) -> Student:
        """Create and stage a new student."""
        student = Student(
            student_number=student_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            course=course,
            enrolment_date=enrolment_date,
        )
        db.session.add(student)
        return student

    def list_all(self) -> list[Student]:
        """Return all students ordered by last and first name."""
        return Student.query.order_by(
            Student.last_name.asc(), Student.first_name.asc()
        ).all()

    def get_by_id(self, student_id: int) -> Student | None:
        """Return a student by primary key."""
        return db.session.get(Student, student_id)

    def get_by_student_number(self, student_number: str) -> Student | None:
        """Return a student by student number."""
        return Student.query.filter_by(student_number=student_number).first()

    def get_by_email(self, email: str) -> Student | None:
        """Return a student by email address."""
        return Student.query.filter_by(email=email).first()

    def update(self, student: Student, **fields) -> Student:
        """Update a staged student with validated fields."""
        for field, value in fields.items():
            setattr(student, field, value)
        return student

    def delete(self, student: Student) -> None:
        """Delete a staged student."""
        db.session.delete(student)
