from unittest.mock import Mock

import pytest

from frictionless import Checklist, Package, Report, Resource, Schema, Validator


@pytest.mark.parametrize("kind", ["resource", "package"])
@pytest.mark.parametrize("valid", [True, False])
def test_validator_returns_report(kind, valid):
    resource = Resource(
        name="records",
        data=[["id"], [1 if valid else "invalid"]],
        schema=Schema.from_descriptor({"fields": [{"name": "id", "type": "integer"}]}),
    )
    target = Package(resources=[resource]) if kind == "package" else resource

    report = getattr(Validator(), f"validate_{kind}")(target)

    assert isinstance(report, Report)
    assert report.valid is valid
    assert report.flatten(["type"]) == ([] if valid else [["type-error"]])


@pytest.mark.parametrize("target_class", [Resource, Package])
def test_validator_forwards_arguments_and_report(target_class, monkeypatch):
    target = target_class()
    report = Report.from_validation()
    validate = Mock(return_value=report)
    monkeypatch.setattr(target, "validate", validate)
    checklist = Checklist()

    result = getattr(Validator(), f"validate_{target_class.__name__.lower()}")(
        target, checklist, limit_rows=1, limit_errors=2
    )

    assert result is report
    validate.assert_called_once_with(checklist, limit_rows=1, limit_errors=2)


@pytest.mark.parametrize("target_class", [Resource, Package])
def test_validator_propagates_exceptions(target_class, monkeypatch):
    target = target_class()
    error = ValueError("validation failed")
    validate = Mock(side_effect=error)
    monkeypatch.setattr(target, "validate", validate)

    with pytest.raises(ValueError) as exception:
        getattr(Validator(), f"validate_{target_class.__name__.lower()}")(target)

    assert exception.value is error
    validate.assert_called_once_with()
