import pytest

from frictionless import Field, Schema

# General


def test_field_to_copy():
    source = Field.from_descriptor({"name": "name", "type": "integer"})
    target = source.to_copy()
    assert source is not target
    assert source == target


# Missing values
#
# `to_descriptor` returns a canonical form: the information (values, labels)
# is preserved, the notation is not. Object entries are emitted only when at
# least one label exists; otherwise the entries canonicalize to plain strings.

MISSING_VALUES_EXPORT_CASES = [
    ("strings", ["", "NA"], ["", "NA"]),
    (
        "objects-with-labels",
        [{"value": "-99", "label": "REFUSED"}, {"value": ""}],
        [{"value": "-99", "label": "REFUSED"}, {"value": ""}],
    ),
    ("objects-without-labels", [{"value": "-"}], ["-"]),
]


@pytest.mark.parametrize(
    "name, source, expected",
    MISSING_VALUES_EXPORT_CASES,
    ids=[case[0] for case in MISSING_VALUES_EXPORT_CASES],
)
def test_field_to_descriptor_missing_values_canonical_form(name, source, expected):
    descriptor = {"name": "name", "type": "string", "missingValues": source}
    exported = Field.from_descriptor(descriptor).to_descriptor()["missingValues"]
    assert exported == expected
    # the canonical form is a fixed point: re-importing it exports identically
    reimported = Field.from_descriptor(
        {"name": "name", "type": "string", "missingValues": exported}
    )
    assert reimported.to_descriptor()["missingValues"] == exported


def test_field_set_schema():
    schema_prev = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    field = Field(name="name", schema=schema_prev)
    assert field.schema == schema_prev
    schema_next = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    field.schema = schema_next
    assert field.schema == schema_next
