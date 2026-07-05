"""Main application routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.example_service import RecordService

main_bp = Blueprint("main", __name__)
service = RecordService()


@main_bp.get("/")
def index() -> str:
    """Render the main page with existing records."""
    records = service.list_records()
    return render_template("index.html", records=records)


@main_bp.post("/records")
def create_record():
    """Create a new record via the service layer."""
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    try:
        service.create_record(name=name, description=description)
    except ValueError as exc:
        flash(str(exc), "error")
        records = service.list_records()
        return render_template("index.html", records=records, form_error=str(exc)), 400
    except RuntimeError as exc:
        flash(str(exc), "error")
        records = service.list_records()
        return render_template("index.html", records=records, form_error=str(exc)), 500

    flash("Record created successfully.", "success")
    return redirect(url_for("main.index"))
