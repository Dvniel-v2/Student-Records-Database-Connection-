"""Main application routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.security.csrf import validate_csrf
from app.services.academic_record_service import (
    AcademicRecordService,
    AcademicRecordServiceError,
    RecordPage,
)
from app.services.approved_student_service import (
    ApprovedStudentService,
    ApprovedStudentServiceError,
    ApprovedStudentValidationError,
)
from app.services.assignment_report_service import (
    AssignmentReportService,
    AssignmentReportServiceError,
    AssignmentReportValidationError,
)
from app.services.dashboard_service import DashboardService, DashboardServiceError
from app.services.student_write_service import (
    StudentWriteConflictError,
    StudentWriteService,
    StudentWriteServiceError,
    StudentWriteValidationError,
)

main_bp = Blueprint("main", __name__)
student_service = ApprovedStudentService()
dashboard_service = DashboardService()
academic_service = AcademicRecordService()
student_write_service = StudentWriteService()
assignment_report_service = AssignmentReportService()

DATABASE_UNAVAILABLE_MESSAGE = (
    "Student records are currently unavailable. "
    "Check the local database connection and PostgreSQL setup."
)


@main_bp.app_context_processor
def inject_assignment_reports() -> dict[str, list]:
    """Expose report definitions to shared navigation."""
    return {"navigation_reports": assignment_report_service.catalogue()}


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
    """Render searchable, paginated Student Directory records."""
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


@main_bp.get("/students/new")
def new_student_form() -> str:
    """Render the student creation form."""
    try:
        choices = student_write_service.form_choices()
    except StudentWriteServiceError:
        flash("Student form reference data is currently unavailable.", "error")
        return redirect(url_for("main.students")), 302
    return render_template(
        "add_student.html",
        form={},
        errors={},
        choices=choices,
    )


@main_bp.get("/courses")
def courses() -> str:
    """Render approved course catalogue records."""
    return _render_record_page("courses_page", "Course records are unavailable.")


@main_bp.get("/modules")
def modules() -> str:
    """Render approved module offering records."""
    return _render_record_page("modules_page", "Module records are unavailable.")


@main_bp.get("/enrolments")
def enrolments() -> str:
    """Render approved enrolment records."""
    return _render_record_page("enrolments_page", "Enrolment records are unavailable.")


@main_bp.get("/grades")
def grades() -> str:
    """Render approved grade records."""
    return _render_record_page("grades_page", "Grade records are unavailable.")


@main_bp.get("/reports")
def reports() -> str:
    """Render the report catalogue."""
    return render_template(
        "reports.html", reports=assignment_report_service.catalogue()
    )


@main_bp.get("/reports/<report_key>")
def report_detail(report_key: str) -> str:
    """Render and optionally run one report."""
    has_run = request.args.get("run") == "1"
    try:
        report = assignment_report_service.build_report(
            report_key, request.args.to_dict(), has_run=has_run
        )
    except AssignmentReportValidationError:
        flash("Report not found.", "error")
        return redirect(url_for("main.reports")), 302
    except AssignmentReportServiceError:
        flash("Report data is currently unavailable.", "error")
        return redirect(url_for("main.reports")), 302
    return render_template("report_detail.html", report=report)


@main_bp.post("/students")
def create_student():
    """Create a student in the approved normalised PostgreSQL schema."""
    validate_csrf()
    form = request.form.to_dict()
    try:
        student_id = student_write_service.create_student(form)
    except StudentWriteValidationError as exc:
        choices = student_write_service.form_choices()
        return (
            render_template(
                "add_student.html",
                form=form,
                errors=exc.errors,
                choices=choices,
            ),
            400,
        )
    except StudentWriteConflictError as exc:
        choices = student_write_service.form_choices()
        return (
            render_template(
                "add_student.html",
                form=form,
                errors={"student_number": str(exc)},
                choices=choices,
            ),
            409,
        )
    except StudentWriteServiceError:
        flash("Student record could not be created.", "error")
        return redirect(url_for("main.students")), 302

    flash("Student record created.", "success")
    return redirect(url_for("main.view_student", student_id=student_id)), 302


@main_bp.get("/students/<int:student_id>")
def view_student(student_id: int):
    """Show a single student record."""
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
    """Render the student edit form."""
    try:
        student = student_write_service.get_student_for_edit(student_id)
        choices = student_write_service.form_choices()
    except StudentWriteServiceError:
        flash("Student edit data is currently unavailable.", "error")
        return redirect(url_for("main.view_student", student_id=student_id)), 302

    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("main.students")), 302
    return render_template(
        "edit_student.html",
        student=student,
        form=_student_form_defaults(student),
        errors={},
        choices=choices,
    )


@main_bp.post("/students/<int:student_id>/edit")
def edit_student(student_id: int):
    """Update a student in the approved normalised PostgreSQL schema."""
    validate_csrf()
    form = request.form.to_dict()
    try:
        student_write_service.update_student(student_id, form)
    except StudentWriteValidationError as exc:
        student = student_write_service.get_student_for_edit(student_id)
        if student is None:
            flash("Student not found.", "error")
            return redirect(url_for("main.students")), 302
        choices = student_write_service.form_choices()
        return (
            render_template(
                "edit_student.html",
                student=student,
                form=form,
                errors=exc.errors,
                choices=choices,
            ),
            400,
        )
    except StudentWriteConflictError as exc:
        student = student_write_service.get_student_for_edit(student_id)
        choices = student_write_service.form_choices()
        return (
            render_template(
                "edit_student.html",
                student=student,
                form=form,
                errors={"student_number": str(exc)},
                choices=choices,
            ),
            409,
        )
    except StudentWriteServiceError:
        flash("Student record could not be updated.", "error")
        return redirect(url_for("main.view_student", student_id=student_id)), 302

    flash("Student record updated.", "success")
    return redirect(url_for("main.view_student", student_id=student_id)), 302


@main_bp.get("/students/<int:student_id>/withdraw")
def withdraw_student_confirm(student_id: int):
    """Render Student withdrawal confirmation."""
    try:
        student = student_service.get_student(student_id)
    except (ApprovedStudentValidationError, ApprovedStudentServiceError):
        flash(DATABASE_UNAVAILABLE_MESSAGE, "error")
        return redirect(url_for("main.students")), 302
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("main.students")), 302
    return render_template("withdraw_student.html", student=student)


@main_bp.post("/students/<int:student_id>/withdraw")
def withdraw_student(student_id: int):
    """Withdraw a Student without deleting academic history."""
    validate_csrf()
    try:
        student_write_service.withdraw_student(student_id)
    except StudentWriteValidationError:
        flash("Student not found.", "error")
        return redirect(url_for("main.students")), 302
    except StudentWriteServiceError:
        flash("Student could not be withdrawn.", "error")
        return redirect(url_for("main.view_student", student_id=student_id)), 302

    flash("Student record withdrawn.", "success")
    return redirect(url_for("main.view_student", student_id=student_id)), 302


@main_bp.get("/students/<int:student_id>/delete")
def legacy_withdraw_student_confirm_redirect(student_id: int):
    """Redirect legacy delete URLs to the withdrawal confirmation route."""
    return (
        redirect(url_for("main.withdraw_student_confirm", student_id=student_id)),
        301,
    )


@main_bp.post("/students/<int:student_id>/delete")
def legacy_withdraw_student_redirect(student_id: int):
    """Redirect legacy delete submissions to the withdrawal route."""
    return redirect(url_for("main.withdraw_student", student_id=student_id)), 308


def _int_arg(name: str, default: int) -> int:
    """Return a positive integer query argument."""
    try:
        return max(int(request.args.get(name, default)), 1)
    except (TypeError, ValueError):
        return default


def _render_record_page(service_method: str, error_message: str) -> str:
    """Render one read-only approved academic record page."""
    try:
        page = getattr(academic_service, service_method)()
    except AcademicRecordServiceError:
        flash(error_message, "error")
        page = RecordPage(
            title="Records unavailable",
            subtitle="Records could not be read",
            description="Check the local database connection and PostgreSQL setup.",
            columns=[],
            rows=[],
        )
    return render_template("records.html", page=page)


def _student_form_defaults(student) -> dict[str, str]:
    """Return editable Student values for form inputs."""
    return {
        "student_number": student.student_number,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": "",
        "phone": student.phone or "",
        "nationality": student.nationality or "",
        "programme_code": student.programme_code,
        "date_of_birth": student.date_of_birth,
        "enrolment_year": str(student.enrolment_year),
        "year_of_study": str(student.year_of_study),
        "admission_type": student.admission_type,
        "student_status": student.student_status,
        "graduation_status": student.graduation_status,
    }
