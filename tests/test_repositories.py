"""Tests for the student repository layer."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.repositories.student_repository import StudentRepository


def _create_student(repository: StudentRepository, **overrides):
    student_attrs = {
        "student_number": "SR1001",
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "course": "Computer Science",
        "enrolment_date": date(2024, 9, 16),
    }
    student_attrs.update(overrides)
    student = repository.create(**student_attrs)
    db.session.commit()
    return student


def test_repository_creates_and_gets_student(app):
    repository = StudentRepository()
    student = _create_student(repository)

    assert repository.get_by_id(student.id).email == "ada@example.com"
    assert repository.get_by_student_number("SR1001").id == student.id


def test_repository_lists_students(app):
    repository = StudentRepository()
    _create_student(repository, student_number="SR1001", email="ada@example.com")
    _create_student(
        repository,
        student_number="SR1002",
        first_name="Grace",
        last_name="Hopper",
        email="grace@example.com",
    )

    assert len(repository.list_all()) == 2


def test_repository_updates_student(app):
    repository = StudentRepository()
    student = _create_student(repository)

    repository.update(student, course="Data Analytics")
    db.session.commit()

    assert repository.get_by_id(student.id).course == "Data Analytics"


def test_repository_deletes_student(app):
    repository = StudentRepository()
    student = _create_student(repository)

    repository.delete(student)
    db.session.commit()

    assert repository.get_by_id(student.id) is None


def test_repository_duplicate_student_number_raises(app):
    repository = StudentRepository()
    _create_student(repository)

    repository.create(
        student_number="SR1001",
        first_name="Alan",
        last_name="Turing",
        email="alan@example.com",
        course="Cyber Security",
        enrolment_date=date(2024, 9, 16),
    )

    with pytest.raises(IntegrityError):
        db.session.commit()
