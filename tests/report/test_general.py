import pprint
from frictionless import validate, helpers


IS_UNIX = not helpers.is_platform("windows")


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
    assert report.task.resource.path == "data/table.csv"
    assert report.task.resource.scheme == "file"
    assert report.task.resource.format == "csv"
    assert report.task.resource.hashing == "md5"
    assert report.task.resource.encoding == "utf-8"
    assert report.task.resource.innerpath == ""
    assert report.task.resource.compression == ""
    assert report.task.resource.dialect == {}
    assert report.task.resource.layout == {}
    assert report.task.resource.header == ["id", "name"]
    assert report.task.resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }
    if IS_UNIX:
        assert report.task.resource.stats == {
            "hash": "6c2c61dd9b0e9c6876139a449ed87933",
            "bytes": 30,
            "fields": 2,
            "rows": 2,
        }
    assert report.task.time
    assert report.task.valid is True
    assert report.task.scope == [
        # File
        "hash-count-error",
        "byte-count-error",
        # Table
        "field-count-error",
        "row-count-error",
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
        "primary-key-error",
        "foreign-key-error",
        # Cell
        "extra-cell",
        "missing-cell",
        "type-error",
        "constraint-error",
        "unique-error",
    ]
    assert report.task.stats == {
        "errors": 0,
    }
    assert report.errors == []


def test_report_expand():
    report = validate("data/table.csv")
    report.expand()
    assert report.task.resource.schema == {
        "fields": [
            {"name": "id", "type": "integer", "format": "default", "bareNumber": True},
            {"name": "name", "type": "string", "format": "default"},
        ],
        "missingValues": [""],
    }


# Import/Export


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


# Issues


def test_report_pprint_1029():
    report = validate("data/capital-invalid.csv", pick_errors=["duplicate-label"])
    assert repr(report) == pprint.pformat(report)
