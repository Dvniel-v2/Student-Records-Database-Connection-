"""Tests for the model layer."""

from app.models.example_model import Record


def test_record_model_can_be_instantiated():
    record = Record(name="Test", description="Model test")

    assert record.name == "Test"
    assert record.description == "Model test"
    assert record.to_dict()["name"] == "Test"
