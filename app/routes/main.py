"""Main application routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.approved_student_service import (
    ApprovedStudentService,
    ApprovedStudentServiceError,
    ApprovedStudentValidationError,
)
from app.services.dashboard_service import DashboardService, DashboardServiceError

main_bp = Blueprint("main", __name__)
student_service = ApprovedStudentService()
dashboard_service = DashboardService()

DATABASE_UNAVAILABLE_MESSAGE = (
    "Approved PostgreSQL student records are currently unavailable. "
    "Check the local database connection and approved schema configuration."
)


@main_bp.get("/")
def index() -> str:
    """Render the dashboard."""
    try:
        dashboard = dashboard_service.get_dashboard()
        database_connected = True
    except DashboardServiceError:
        flash(DATABASE_UNAVAILABLE_MESSAGE, "error")
        dashboard = None
        database_connected = False
    return render_template(
        "dashboard.html",
        dashboard=dashboard,
        database_connected=database_connected,
    )


@main_bp.get("/students")
def students() -> str:
    """Render searchable, paginated approved Student Directory records."""
    filters = {
        "q": request.args.get("q", "").strip(),
        "programme": request.args.get("programme", "").strip(),
        "status": request.args.get("status", "").strip(),
        "page": _int_arg("page", 1),
        "per_page": _int_arg("per_page", 25),
    }
    try:
        result = student_service.search_students(
            search_term=filters["q"],
            programme_code=filters["programme"],
            status=filters["status"],
            page=filters["page"],
            per_page=filters["per_page"],
        )
        programmes = student_service.list_programmes()
        statuses = student_service.list_statuses()
        summary = student_service.get_status_summary()
    except ApprovedStudentServiceError:
        flash(DATABASE_UNAVAILABLE_MESSAGE, "error")
        result = None
        programmes = []
        statuses = []
        summary = None

    return render_template(
        "students.html",
        result=result,
        programmes=programmes,
        statuses=statuses,
        summary=summary,
        filters=filters,
        per_page_options=student_service.PER_PAGE_OPTIONS,
    )


@main_bp.post("/students")
def create_student():
    """Keep creation unavailable until normalised PostgreSQL writes exist."""
    flash(
        "Student record creation is not yet available for the normalised "
        "PostgreSQL schema.",
        "error",
    )
    return redirect(url_for("main.students"))


@main_bp.get("/students/<int:student_id>")
def view_student(student_id: int):
    """Show a single approved student record."""
    try:
        student = student_service.get_student(student_id)
    except ApprovedStudentValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.students")), 302
    except ApprovedStudentServiceError:
        flash(DATABASE_UNAVAILABLE_MESSAGE, "error")
        return redirect(url_for("main.students")), 302

    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("main.students")), 302
    return render_template("student_detail.html", student=student)


@main_bp.get("/students/<int:student_id>/edit")
def edit_student_form(student_id: int):
    """Keep editing unavailable until normalised PostgreSQL writes exist."""
    flash(
        "Student editing is not yet available for the normalised " "PostgreSQL schema.",
        "error",
    )
    return redirect(url_for("main.view_student", student_id=student_id)), 302


@main_bp.post("/students/<int:student_id>/edit")
def edit_student(student_id: int):
    """Keep updates unavailable until normalised PostgreSQL writes exist."""
    flash(
        "Student editing is not yet available for the normalised " "PostgreSQL schema.",
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


def _int_arg(name: str, default: int) -> int:
    """Return a positive integer query argument."""
    try:
        return max(int(request.args.get(name, default)), 1)
    except (TypeError, ValueError):
        return default
