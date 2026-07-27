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


NAME_MATCHED = ["equal", "subset", "superset", "partial"]


def _make_header(labels, field_names, *, fields_match="exact", ignore_case=False):
    return Header(
        labels,
        fields=[fields.AnyField(name=name) for name in field_names],
        row_numbers=[1],
        ignore_case=ignore_case,
        fields_match=fields_match,
    )


@pytest.mark.parametrize(
    "labels, field_names, fields_match, ignore_case, expected_names",
    [
        pytest.param(
            ["a", "b"],
            ["a", "b"],
            "exact",
            False,
            ["a", "b"],
            id="exact: schema fields are returned as-is",
        ),
        pytest.param(
            ["b", "a"],
            ["a", "b"],
            "exact",
            False,
            ["a", "b"],
            id="exact: schema order is kept even if labels differ",
        ),
        pytest.param(
            ["a", "extra"],
            ["a"],
            "exact",
            False,
            ["a"],
            id="exact: extra labels get no field",
        ),
        *[
            pytest.param(
                ["b", "a"],
                ["a", "b"],
                mode,
                False,
                ["b", "a"],
                id=f"{mode}: fields are reordered to match labels",
            )
            for mode in NAME_MATCHED
        ],
        *[
            pytest.param(
                ["a", "extra"],
                ["a"],
                mode,
                False,
                ["a", "extra"],
                id=f"{mode}: extra labels get a default any-typed field",
            )
            for mode in NAME_MATCHED
        ],
        *[
            pytest.param(
                ["a"],
                ["a", "b"],
                mode,
                False,
                ["a"],
                id=f"{mode}: fields absent from labels are dropped",
            )
            for mode in NAME_MATCHED
        ],
        pytest.param(
            ["B", "A"],
            ["a", "b"],
            "partial",
            True,
            ["b", "a"],
            id="partial + ignore_case: matching is case-insensitive",
        ),
    ],
)
def test_get_expected_fields(
    labels, field_names, fields_match, ignore_case, expected_names
):
    header = _make_header(
        labels, field_names, fields_match=fields_match, ignore_case=ignore_case
    )
    actual = [f.name for f in header.get_expected_fields()]
    assert actual == expected_names


@pytest.mark.parametrize("fields_match", NAME_MATCHED)
def test_get_expected_fields_default_field_is_any_typed(fields_match):
    header = _make_header(["a", "extra"], ["a"], fields_match=fields_match)
    expected = header.get_expected_fields()
    assert expected[1].type == "any"


@pytest.mark.parametrize("fields_match", NAME_MATCHED)
def test_get_expected_fields_raises_on_duplicate_labels(fields_match):
    header = _make_header(["a", "a"], ["a"], fields_match=fields_match)
    with pytest.raises(frictionless.FrictionlessException):
        header.get_expected_fields()


def test_get_expected_fields_exact_tolerates_duplicate_labels():
    # Mapping is positional, so duplicates are unambiguous here; they are
    # reported as a `duplicate-label` error rather than raising.
    header = _make_header(["a", "a"], ["a", "b"], fields_match="exact")
    assert [f.name for f in header.get_expected_fields()] == ["a", "b"]


# Tolerated and reported header mismatches, per fieldsMatch value


def _errors(header):
    return [(e.type, e.label, e.field_name, e.field_number) for e in header.errors]


def _make_header_with_required(labels, field_names, required, *, fields_match):
    schema = Schema(
        fields=[
            fields.AnyField(
                name=name, constraints={"required": True} if name in required else {}
            )
            for name in field_names
        ],
        fields_match=fields_match,
    )
    return Header(
        labels,
        fields=schema.fields,
        row_numbers=[1],
        fields_match=fields_match,
    )


EXTRA_LABEL = ("extra-label", "extra", "", 3)
MISSING_LABEL_B = ("missing-label", "", "b", 2)


@pytest.mark.parametrize(
    "fields_match, expected",
    [
        ("exact", [EXTRA_LABEL]),
        ("equal", [EXTRA_LABEL]),
        ("superset", [EXTRA_LABEL]),
        ("subset", []),
        ("partial", []),
    ],
)
def test_errors_on_extra_label(fields_match, expected):
    header = _make_header(["a", "b", "extra"], ["a", "b"], fields_match=fields_match)
    assert _errors(header) == expected


@pytest.mark.parametrize(
    "fields_match, expected",
    [
        ("exact", [MISSING_LABEL_B]),
        ("equal", [MISSING_LABEL_B]),
        ("subset", [MISSING_LABEL_B]),
        ("superset", []),
        ("partial", []),
    ],
)
def test_errors_on_missing_field(fields_match, expected):
    header = _make_header(["a"], ["a", "b"], fields_match=fields_match)
    assert _errors(header) == expected


@pytest.mark.parametrize("fields_match", ["superset", "partial"])
def test_errors_on_missing_required_field(fields_match):
    # Required fields are mandatory even for "superset" and "partial" fieldsMatch.
    header = _make_header_with_required(
        ["a"], ["a", "b"], required=["b"], fields_match=fields_match
    )
    assert _errors(header) == [MISSING_LABEL_B]


@pytest.mark.parametrize("fields_match", NAME_MATCHED)
def test_errors_reordered_labels_are_not_a_mismatch(fields_match):
    header = _make_header(["b", "a"], ["a", "b"], fields_match=fields_match)
    assert _errors(header) == []


def test_errors_exact_reports_reordered_labels_as_incorrect():
    header = _make_header(["b", "a"], ["a", "b"], fields_match="exact")
    assert _errors(header) == [
        ("incorrect-label", "b", "a", 1),
        ("incorrect-label", "a", "b", 2),
    ]


def test_errors_partial_requires_at_least_one_matching_field():
    header = _make_header(["x", "y"], ["a", "b"], fields_match="partial")
    assert [e.type for e in header.errors] == ["unmatched-header"]


def test_errors_partial_accepts_a_single_matching_field():
    header = _make_header(["x", "a"], ["a", "b"], fields_match="partial")
    assert header.errors == []


def test_errors_partial_with_a_schema_without_fields():
    # Nothing is declared, so there is nothing to match: not an error.
    header = _make_header(["x"], [], fields_match="partial")
    assert header.errors == []


@pytest.mark.parametrize("fields_match", ["exact", "equal", "subset", "superset"])
def test_errors_unmatched_header_is_specific_to_partial(fields_match):
    header = _make_header(["x", "y"], ["a", "b"], fields_match=fields_match)
    assert "unmatched-header" not in [e.type for e in header.errors]


def test_errors_extra_label_is_reported_at_its_position_in_the_data():
    header = _make_header(["extra", "a", "b"], ["a", "b"], fields_match="equal")
    assert _errors(header) == [("extra-label", "extra", "", 1)]


# The schema below declares a single field, so a header that doesn't carry it
# shares nothing with the schema: `partial` reports that as an
# `unmatched-header`.
UNMATCHED = ["unmatched-header", "missing-label"]


@pytest.mark.parametrize(
    "source, required, valid_report, nb_errors, types_errors_expected, header_case",
    [
        ([["B"], ["foo"]], {"required": True}, False, 2, UNMATCHED, True),
        ([["B"], ["foo"]], {}, False, 2, UNMATCHED, True),
        ([["a"], ["foo"]], {"required": True}, False, 2, UNMATCHED, True),
        ([["a"], ["foo"]], {}, False, 2, UNMATCHED, True),
        # Ignore header_case
        ([["B"], ["foo"]], {"required": True}, False, 2, UNMATCHED, False),
        ([["B"], ["foo"]], {}, False, 2, UNMATCHED, False),
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
