"""Health-check routes."""

from flask import Blueprint, jsonify

from app.services.database_health_service import DatabaseHealthService

health_bp = Blueprint("health", __name__)
database_health_service = DatabaseHealthService()


@health_bp.get("/health/database")
def database_health():
    """Return approved PostgreSQL schema health without rendering a page."""
    result = database_health_service.check()
    status_code = 200 if result.ok else 503
    return jsonify(result.to_dict()), status_code
