"""Tests for the service layer."""

from app.services.example_service import RecordService


def test_service_creates_record(app):
    service = RecordService()
    record = service.create_record(name="Grace", description="Service test")

    assert record.name == "Grace"
    assert record.description == "Service test"


def test_service_rejects_short_name(app):
    service = RecordService()

    try:
        service.create_record(name="A", description="Testing")
    except ValueError as exc:
        assert "at least 2 characters" in str(exc)
    else:
        raise AssertionError("Service should reject short names")
