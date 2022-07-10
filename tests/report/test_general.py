import pprint
from frictionless import Resource, Checklist, helpers


# General


def test_report():
    resource = Resource("data/table.csv")
    report = resource.validate()
    # Report
    assert report.valid is True
    assert report.stats["time"]
    assert report.stats["errors"] == 0
    assert report.stats["tasks"] == 1
    assert report.errors == []
    # Task
    assert report.task.valid is True
    assert report.task.name == "table"
    assert report.task.place == "data/table.csv"
    assert report.task.tabular is True
    assert report.task.stats["time"]
    assert report.task.stats["errors"] == 0
    if not helpers.is_platform("windows"):
        assert report.task.stats["bytes"] == 30
    assert report.task.stats["fields"] == 2
    assert report.task.stats["rows"] == 2
    if not helpers.is_platform("windows"):
        assert report.task.stats["hash"] == "6c2c61dd9b0e9c6876139a449ed87933"
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
    assert report.warnings == []
    assert report.errors == []


def test_report_pprint():
    resource = Resource("data/capital-invalid.csv")
    checklist = Checklist(pick_errors=["duplicate-label"])
    report = resource.validate(checklist)
    assert repr(report) == pprint.pformat(report)
