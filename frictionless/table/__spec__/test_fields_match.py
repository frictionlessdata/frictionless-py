import pytest

from frictionless import Checklist, Detector, Schema, fields
from frictionless.resources import TableResource

# The deprecated `schema_sync` option, and how it arbitrates with the
# `fieldsMatch` property that replaces it.
#
# `data/sync-schema.csv` carries two columns, `name` and `id`, while the
# schemas below declare `name` alone: whether the undeclared column is
# tolerated tells which mode was actually applied.


def _validate(schema, *, schema_sync):
    """Validate, keeping the header verdict only.

    Cell errors are filtered out on purpose: under `exact` an undeclared
    column also raises an `extra-cell` on every row, which is a known bug
    (characterized in `resource/__spec__/test_validate_schema.py`) and is not
    what these tests are about.
    """
    resource = TableResource(
        path="data/sync-schema.csv",
        schema=schema,
        detector=Detector(schema_sync=schema_sync),
    )
    return resource.validate(Checklist(pick_errors=["#header"]))


def _schema(fields_match=None):
    descriptor = {"fields": [{"name": "name", "type": "string"}]}
    if fields_match is not None:
        descriptor["fieldsMatch"] = fields_match
    return Schema.from_descriptor(descriptor)


def test_resource_without_schema_sync_does_not_warn(recwarn):
    report = _validate(_schema(), schema_sync=False)
    assert report.flatten(["type", "label"]) == [["extra-label", "id"]]
    assert len(recwarn) == 0


def test_resource_schema_sync_is_deprecated():
    with pytest.warns(DeprecationWarning, match="--schema-sync"):
        report = _validate(_schema(), schema_sync=True)
    # Resolved to `partial`, which tolerates the undeclared column.
    assert report.valid


def test_resource_fields_match_takes_precedence_over_schema_sync(recwarn):
    report = _validate(_schema("equal"), schema_sync=True)
    # `equal` rejects the undeclared column where schema_sync would tolerate it.
    assert report.flatten(["type", "label"]) == [["extra-label", "id"]]
    assert [warning.category for warning in recwarn] == [UserWarning]
    assert "takes precedence" in str(recwarn[0].message)


def test_resource_explicit_exact_takes_precedence_over_schema_sync(recwarn):
    # Declaring the default explicitly is a decision too: it disables the
    # deprecated option rather than being mistaken for "nothing declared".
    report = _validate(_schema("exact"), schema_sync=True)
    assert report.flatten(["type", "label"]) == [["extra-label", "id"]]
    assert [warning.category for warning in recwarn] == [UserWarning]


def test_resource_schema_sync_on_an_inferred_schema_is_deprecated():
    # No schema at all: nothing is declared, so the option still applies.
    resource = TableResource(
        path="data/sync-schema.csv", detector=Detector(schema_sync=True)
    )
    with pytest.warns(DeprecationWarning, match="--schema-sync"):
        assert resource.validate().valid


def test_resource_fields_match_without_schema_sync_needs_no_detector():
    schema = Schema(fields=[fields.AnyField(name="name")], fields_match="subset")
    with TableResource(path="data/sync-schema.csv", schema=schema) as resource:
        assert resource.header.valid
