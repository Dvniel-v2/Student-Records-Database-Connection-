"""Main application routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.student_service import (
    StudentService,
    StudentServiceError,
    StudentValidationError,
)

main_bp = Blueprint("main", __name__)
service = StudentService()


@main_bp.get("/")
def index() -> str:
    """Render the main page with existing students."""
    students = service.list_students()
    return render_template("index.html", students=students)


@main_bp.post("/students")
def create_student():
    """Create a new student via the service layer."""
    try:
        service.create_student(**request.form.to_dict())
    except StudentValidationError as exc:
        flash(str(exc), "error")
        students = service.list_students()
        return render_template("index.html", students=students, form=request.form), 400
    except StudentServiceError as exc:
        flash(str(exc), "error")
        students = service.list_students()
        return render_template("index.html", students=students, form=request.form), 500

    flash("Student created successfully.", "success")
    return redirect(url_for("main.index"))


@main_bp.get("/students/<int:student_id>")
def view_student(student_id: int):
    """Show a single student."""
    student = service.get_student(student_id)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("main.index")), 302
    return render_template("student_detail.html", student=student)


@main_bp.get("/students/<int:student_id>/edit")
def edit_student_form(student_id: int):
    """Render the edit form for a student."""
    student = service.get_student(student_id)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("main.index")), 302
    return render_template("edit_student.html", student=student)


@main_bp.post("/students/<int:student_id>/edit")
def edit_student(student_id: int):
    """Update a student via the service layer."""
    student = service.get_student(student_id)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("main.index")), 302

    try:
        student = service.update_student(student_id, **request.form.to_dict())
    except StudentValidationError as exc:
        flash(str(exc), "error")
        return (
            render_template("edit_student.html", student=student, form=request.form),
            400,
        )
    except StudentServiceError as exc:
        flash(str(exc), "error")
        return (
            render_template("edit_student.html", student=student, form=request.form),
            500,
        )

    flash("Student updated successfully.", "success")
    return redirect(url_for("main.view_student", student_id=student.id))


@main_bp.get("/students/<int:student_id>/delete")
def delete_student_confirm(student_id: int):
    """Render a confirmation screen before deleting a student."""
    student = service.get_student(student_id)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("main.index")), 302
    return render_template("delete_student.html", student=student)


@main_bp.post("/students/<int:student_id>/delete")
def delete_student(student_id: int):
    """Delete a student via the service layer."""
    try:
        service.delete_student(student_id)
    except StudentValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index")), 302
    except StudentServiceError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index")), 302

    flash("Student deleted successfully.", "success")
    return redirect(url_for("main.index"))
