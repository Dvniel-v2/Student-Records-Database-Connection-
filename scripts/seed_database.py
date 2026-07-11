"""Seed the database with realistic student records."""

from __future__ import annotations

import os

from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.extensions import db
from app.models.student import Student

STUDENT_COUNT = 10


def seed_database() -> None:
    """Populate the database with realistic students safely."""
    if os.getenv("ALLOW_LEGACY_STUDENT_SEED") != "true":
        raise RuntimeError(
            "This script seeds the legacy simplified students table only. "
            "Set ALLOW_LEGACY_STUDENT_SEED=true for isolated local development."
        )

    app = create_app("development")
    with app.app_context():
        fake = Faker()
        inserted = 0

        while inserted < STUDENT_COUNT:
            student_number = fake.unique.bothify(text="SR####")
            email = fake.unique.email().lower()
            if Student.query.filter_by(student_number=student_number).first():
                continue
            if Student.query.filter_by(email=email).first():
                continue

            student = Student(
                student_number=student_number,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=email,
                course=fake.random_element(
                    elements=(
                        "Computer Science",
                        "Data Analytics",
                        "Business Management",
                        "Cyber Security",
                        "Software Engineering",
                    )
                ),
                enrolment_date=fake.date_between(start_date="-3y", end_date="today"),
            )
            db.session.add(student)
            inserted += 1

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

        print(f"{inserted} student records inserted successfully.")


if __name__ == "__main__":
    seed_database()
