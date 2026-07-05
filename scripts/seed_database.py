"""Seed the database with sample records."""

from __future__ import annotations

from faker import Faker

from app import create_app
from app.extensions import db
from app.models.example_model import Record


def seed_database() -> None:
    """Populate the database with example records if none exist."""
    app = create_app("development")
    with app.app_context():
        if Record.query.first() is not None:
            print("Database already contains records; skipping seed.")
            return

        fake = Faker()
        for _ in range(3):
            record = Record(name=fake.name(), description=fake.sentence())
            db.session.add(record)

        db.session.commit()
        print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed_database()
