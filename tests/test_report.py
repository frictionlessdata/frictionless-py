import pytest
from frictionless import validate, helpers


# Report


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_report():
    report = validate("data/table.csv")
    # Report
    assert report.version.startswith("3")
    assert report.time
    assert report.valid is True
    assert report.stats == {"errors": 0, "tables": 1}
    assert report.errors == []
    # Table
    assert report.table.path == "data/table.csv"
    assert report.table.scheme == "file"
    assert report.table.format == "csv"
    assert report.table.hashing == "md5"
    assert report.table.encoding == "utf-8"
    assert report.table.compression == "no"
    assert report.table.compression_path == ""
    assert report.table.dialect == {}
    assert report.table.query == {}
    assert report.table.header == ["id", "name"]
    assert report.table.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }
    assert report.table.time
    assert report.table.valid is True
    assert report.table.scope == [
        "dialect-error",
        "schema-error",
        "field-error",
        "extra-label",
        "missing-label",
        "blank-label",
        "duplicate-label",
        "blank-header",
        "incorrect-label",
        "extra-cell",
        "missing-cell",
        "blank-row",
        "type-error",
        "constraint-error",
        "unique-error",
        "primary-key-error",
        "foreign-key-error",
        "checksum-error",
    ]
    assert report.table.stats == {
        "hash": "6c2c61dd9b0e9c6876139a449ed87933",
        "bytes": 30,
        "fields": 2,
        "rows": 2,
        "errors": 0,
    }
    assert report.errors == []


def test_report_expand():
    report = validate("data/table.csv")
    report.expand()
    assert report.table.schema == {
        "fields": [
            {"name": "id", "type": "integer", "format": "default", "bareNumber": True},
            {"name": "name", "type": "string", "format": "default"},
        ],
        "missingValues": [""],
    }
