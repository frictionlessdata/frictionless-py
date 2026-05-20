import pytest

import frictionless
from frictionless import Schema, fields
from frictionless.resources import TableResource
from frictionless.table.header import Header

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


# get_expected_fields


def _make_header(labels, field_names, *, schema_sync=False, ignore_case=False):
    return Header(
        labels,
        fields=[fields.AnyField(name=name) for name in field_names],
        row_numbers=[1],
        ignore_case=ignore_case,
        schema_sync=schema_sync,
    )


@pytest.mark.parametrize(
    "labels, field_names, schema_sync, ignore_case, expected_names",
    [
        pytest.param(
            ["a", "b"], ["a", "b"], False, False, ["a", "b"],
            id="no-sync: schema fields are returned as-is",
        ),
        pytest.param(
            ["b", "a"], ["a", "b"], False, False, ["a", "b"],
            id="no-sync: schema order is kept even if labels differ",
        ),
        pytest.param(
            ["b", "a"], ["a", "b"], True, False, ["b", "a"],
            id="sync: fields are reordered to match labels",
        ),
        pytest.param(
            ["a", "extra"], ["a"], True, False, ["a", "extra"],
            id="sync: extra labels get a default any-typed field",
        ),
        pytest.param(
            ["a"], ["a", "b"], True, False, ["a"],
            id="sync: fields absent from labels are dropped",
        ),
        pytest.param(
            ["B", "A"], ["a", "b"], True, True, ["b", "a"],
            id="sync + ignore_case: matching is case-insensitive",
        ),
    ],
)
def test_get_expected_fields(
    labels, field_names, schema_sync, ignore_case, expected_names
):
    header = _make_header(
        labels, field_names, schema_sync=schema_sync, ignore_case=ignore_case
    )
    actual = [f.name for f in header.get_expected_fields()]
    assert actual == expected_names


def test_get_expected_fields_sync_default_field_is_any_typed():
    header = _make_header(["a", "extra"], ["a"], schema_sync=True)
    expected = header.get_expected_fields()
    assert expected[1].type == "any"


def test_get_expected_fields_sync_raises_on_duplicate_labels():
    header = _make_header(["a", "a"], ["a"], schema_sync=True)
    with pytest.raises(frictionless.FrictionlessException):
        header.get_expected_fields()


@pytest.mark.parametrize(
    "source, required, valid_report, nb_errors, types_errors_expected, header_case",
    [
        ([["B"], ["foo"]], {"required": True}, False, 1, ["missing-label"], True),
        ([["B"], ["foo"]], {}, False, 1, ["missing-label"], True),
        ([["a"], ["foo"]], {"required": True}, False, 1, ["missing-label"], True),
        ([["a"], ["foo"]], {}, False, 1, ["missing-label"], True),
        # Ignore header_case
        ([["B"], ["foo"]], {"required": True}, False, 1, ["missing-label"], False),
        ([["B"], ["foo"]], {}, False, 1, ["missing-label"], False),
        ([["a"], ["foo"]], {"required": True}, True, 0, [], False),
        ([["a"], ["foo"]], {}, True, 0, [], False),
    ],
)
def test_missing_primary_key_label_with_shema_sync_issue_1633(
    source, required, valid_report, nb_errors, types_errors_expected, header_case
):
    schema_descriptor = {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [{"name": "A", "constraints": required}],
        "primaryKey": ["A"],
    }

    resource = TableResource(
        source=source,
        schema=Schema.from_descriptor(schema_descriptor),
        detector=frictionless.Detector(schema_sync=True),
        dialect=frictionless.Dialect(header_case=header_case),
    )

    report = frictionless.validate(resource)

    assert report.valid == valid_report

    if not report.valid:
        errors = report.tasks[0].errors
        assert len(errors) == nb_errors
        for error, type_expected in zip(errors, types_errors_expected):
            assert error.type == type_expected
