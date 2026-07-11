"""Main application routes."""

from flask import Blueprint, flash, redirect, render_template, url_for

from app.services.approved_student_service import (
    ApprovedStudentService,
    ApprovedStudentServiceError,
    ApprovedStudentValidationError,
)

main_bp = Blueprint("main", __name__)
service = ApprovedStudentService()


@main_bp.get("/")
def index() -> str:
    """Render approved read-only student records."""
    try:
        students = service.list_students()
    except ApprovedStudentServiceError as exc:
        flash(str(exc), "error")
        students = []
    return render_template("index.html", students=students)


@main_bp.post("/students")
def create_student():
    """Keep creation unavailable until normalised PostgreSQL writes exist."""
    flash(
        "Student record creation is not yet available for the normalised "
        "PostgreSQL schema.",
        "error",
    )
    return redirect(url_for("main.index"))


@main_bp.get("/students/<int:student_id>")
def view_student(student_id: int):
    """Show a single approved student record."""
    try:
        student = service.get_student(student_id)
    except ApprovedStudentValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index")), 302
    except ApprovedStudentServiceError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index")), 302

    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("main.index")), 302
    return render_template("student_detail.html", student=student)


@main_bp.get("/students/<int:student_id>/edit")
def edit_student_form(student_id: int):
    """Keep editing unavailable until normalised PostgreSQL writes exist."""
    flash(
        "Student editing is not yet available for the normalised "
        "PostgreSQL schema.",
        "error",
    )
    return redirect(url_for("main.view_student", student_id=student_id)), 302


@main_bp.post("/students/<int:student_id>/edit")
def edit_student(student_id: int):
    """Keep updates unavailable until normalised PostgreSQL writes exist."""
    flash(
        "Student editing is not yet available for the normalised "
        "PostgreSQL schema.",
        "error",
    )
    return redirect(url_for("main.view_student", student_id=student_id)), 302


@main_bp.get("/students/<int:student_id>/delete")
def delete_student_confirm(student_id: int):
    """Keep deletion unavailable until normalised PostgreSQL writes exist."""
    flash(
        "Student deletion is not yet available for the normalised "
        "PostgreSQL schema.",
        "error",
    )
    return redirect(url_for("main.view_student", student_id=student_id)), 302


@main_bp.post("/students/<int:student_id>/delete")
def delete_student(student_id: int):
    """Keep deletes unavailable until normalised PostgreSQL writes exist."""
    flash(
        "Student deletion is not yet available for the normalised "
        "PostgreSQL schema.",
        "error",
    )
    return redirect(url_for("main.view_student", student_id=student_id)), 302
