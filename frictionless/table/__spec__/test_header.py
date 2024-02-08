import frictionless
from frictionless import Schema, fields
from frictionless.resources import TableResource

# General


def test_basic():
    with TableResource(data=[["field1", "field2", "field3"], [1, 2, 3]]) as resource:
        header = resource.header
        assert header == ["field1", "field2", "field3"]
        assert header.labels == ["field1", "field2", "field3"]
        assert header.field_numbers == [1, 2, 3]
        assert header.row_numbers == [1]
        assert header.errors == []
        assert header == ["field1", "field2", "field3"]


def test_extra_label():
    schema = Schema(fields=[fields.AnyField(name="id")])
    with TableResource(path="data/table.csv", schema=schema) as resource:
        header = resource.header
        assert header == ["id"]
        assert header.labels == ["id", "name"]
        assert header.valid is False


def test_missing_label():
    schema = Schema(
        fields=[
            fields.AnyField(name="id"),
            fields.AnyField(name="name"),
            fields.AnyField(name="extra"),
        ]
    )
    with TableResource(path="data/table.csv", schema=schema) as resource:
        header = resource.header
        assert header == ["id", "name", "extra"]
        assert header.labels == ["id", "name"]
        assert header.valid is False


def test_missing_primary_key_label_with_shema_sync_issue_1633():
    schema_descriptor = {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [{"name": "A", "constraints": {"required": True}}],
        "primaryKey": ["A"],
    }

    source = [["B"], ["foo"]]

    resource = TableResource(
        source,
        schema=Schema.from_descriptor(schema_descriptor),
        detector=frictionless.Detector(schema_sync=True),
    )

    report = frictionless.validate(resource)

    assert not report.valid
    assert len(report.tasks[0].errors) == 2
    assert report.tasks[0].errors[0].type == "missing-label"
    assert report.tasks[0].errors[1].type == "primary-key"
    
    schema_descriptor = {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [{"name": "A"}],
        "primaryKey": ["A"],
    }

    source = [["B"], ["foo"]]

    resource = TableResource(
        source,
        schema=Schema.from_descriptor(schema_descriptor),
        detector=frictionless.Detector(schema_sync=True),
    )

    report = frictionless.validate(resource)
    assert not report.valid
    assert len(report.tasks[0].errors) == 1
    assert report.tasks[0].errors[0].type == "primary-key"
