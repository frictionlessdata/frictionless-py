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

    test_cases = [
        {
            "constraints": {"required": True},
            "nb_errors": 2,
            "types_errors_expected": ["missing-label", "primary-key"],
        },
        {
            "constraints": {},
            "nb_errors": 1,
            "types_errors_expected": ["primary-key"],
        }
    ]

    for tc in test_cases:
        schema_descriptor = {
            "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
            "fields": [{"name": "A", "constraints": tc["constraints"]}],
            "primaryKey": ["A"],
        }

        resource = TableResource(
            source=[["B"], ["foo"]],
            schema=Schema.from_descriptor(schema_descriptor),
            detector=frictionless.Detector(schema_sync=True),
        )

        report = frictionless.validate(resource)
        errors = report.tasks[0].errors

        assert not report.valid
        assert len(errors) == tc["nb_errors"]
        for error, type_expected in zip(errors, tc["types_errors_expected"]):
            assert error.type == type_expected

    # Ignore header_case
    schema_descriptor = {
            "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
            "fields": [{"name": "A"}],
            "primaryKey": ["A"],
        }

    resource = TableResource(
        source=[["a"], ["foo"]],
        schema=Schema.from_descriptor(schema_descriptor),
        detector=frictionless.Detector(schema_sync=True),
        dialect=frictionless.Dialect(header_case=False)
    )
    report = frictionless.validate(resource)
    assert report.valid
