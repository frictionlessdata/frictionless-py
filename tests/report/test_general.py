import pytest
import pprint
from frictionless import validate, helpers


# General


def test_report():
    report = validate("data/table.csv")
    # Report
    assert report.version.startswith("3") or report.version.startswith("4")
    assert report.time
    assert report.valid is True
    assert report.stats == {"errors": 0, "tasks": 1}
    assert report.errors == []
    # Task
    assert report.task.path == "data/table.csv"
    assert report.task.innerpath == ""
    assert report.task.time
    assert report.task.valid is True
    assert report.task.scope == [
        # File
        "hash-count",
        "byte-count",
        # Table
        "field-count",
        "row-count",
        # Header
        "blank-header",
        # Label
        "extra-label",
        "missing-label",
        "blank-label",
        "duplicate-label",
        "incorrect-label",
        # Row
        "blank-row",
        "primary-key",
        "foreign-key",
        # Cell
        "extra-cell",
        "missing-cell",
        "type-error",
        "constraint-error",
        "unique-error",
    ]
    if not helpers.is_platform("windows"):
        assert report.task.stats == {
            "errors": 0,
            "hash": "6c2c61dd9b0e9c6876139a449ed87933",
            "bytes": 30,
            "fields": 2,
            "rows": 2,
        }
    assert report.errors == []


# TODO: do we need report.expand?
@pytest.mark.skip
def test_report_expand():
    report = validate("data/table.csv")
    report.expand()


# Export/Import


def test_report_to_json_with_bytes_serialization_issue_836():
    source = b"header1,header2\nvalue1,value2\nvalue3,value4"
    report = validate(source)
    descriptor = report.to_json()
    assert descriptor


def test_report_to_yaml_with_bytes_serialization_issue_836():
    source = b"header1,header2\nvalue1,value2\nvalue3,value4"
    report = validate(source)
    descriptor = report.to_yaml()
    assert "binary" not in descriptor


# Problems


def test_report_pprint_1029():
    report = validate("data/capital-invalid.csv", pick_errors=["duplicate-label"])
    assert repr(report) == pprint.pformat(report)
