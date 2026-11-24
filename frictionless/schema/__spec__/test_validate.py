import pytest

from frictionless import Schema

# General


def test_validate():
    report = Schema.validate_descriptor("data/schema.json")
    assert report.valid


def test_validate_invalid():
    report = Schema.validate_descriptor({"fields": "bad"})
    assert report.flatten(["type", "note"]) == [
        [
            "schema-error",
            "'bad' is not of type 'array' at property 'fields'",
        ],
    ]


def test_validate_required_invalid():
    report = Schema.validate_descriptor("data/schema-invalid.json")
    assert report.flatten(["type", "note"]) == [
        [
            "field-error",
            '"required" should be set as "constraints.required"',
        ],
    ]


# Missing values (uniqueness of value and label)
#
# Object entries must have a unique value and an optional unique label;
# absent labels do not collide with each other. Plain string entries keep
# the lax v1 behavior (duplicates allowed).
#
# The object form being a v2 addition, these descriptors declare a v2 `$schema`
# (an absent `$schema` is an explicit v1, which gates the object form out).

MISSING_VALUES_UNIQUENESS_CASES = [
    ("valid-strings", ["", "NA"], []),
    ("valid-duplicate-strings", ["NA", "NA"], []),
    (
        "valid-objects",
        [{"value": "-99", "label": "REFUSED"}, {"value": "", "label": "OMITTED"}],
        [],
    ),
    ("missing-labels-do-not-collide", [{"value": "-99"}, {"value": "-1"}], []),
    (
        "duplicate-value",
        [{"value": "-99", "label": "REFUSED"}, {"value": "-99", "label": "OMITTED"}],
        [["schema-error", 'missing value "-99" is not unique']],
    ),
    (
        "duplicate-label",
        [{"value": "-99", "label": "REFUSED"}, {"value": "", "label": "REFUSED"}],
        [["schema-error", 'missing value label "REFUSED" is not unique']],
    ),
    (
        "duplicate-value-and-label",
        [{"value": "-99", "label": "REFUSED"}, {"value": "-99", "label": "REFUSED"}],
        [
            ["schema-error", 'missing value "-99" is not unique'],
            ["schema-error", 'missing value label "REFUSED" is not unique'],
        ],
    ),
]


@pytest.mark.parametrize(
    "name, source, expected",
    MISSING_VALUES_UNIQUENESS_CASES,
    ids=[case[0] for case in MISSING_VALUES_UNIQUENESS_CASES],
)
def test_validate_missing_values_uniqueness(name, source, expected):
    report = Schema.validate_descriptor(
        {
            "$schema": V2_PROFILE,
            "fields": [{"name": "name", "type": "string"}],
            "missingValues": source,
        }
    )
    assert report.flatten(["type", "note"]) == expected


def test_validate_field_missing_values_uniqueness():
    report = Schema.validate_descriptor(
        {
            "$schema": V2_PROFILE,
            "fields": [
                {
                    "name": "name",
                    "type": "string",
                    "missingValues": [
                        {"value": "-99", "label": "REFUSED"},
                        {"value": "-99", "label": "OMITTED"},
                    ],
                }
            ],
        }
    )
    assert report.flatten(["type", "note"]) == [
        ["field-error", 'missing value "-99" is not unique']
    ]


# Missing values (version gate)
#
# The object form `{value, label?}` is a datapackage v2 addition, rejected
# under v1 — which is also the version of an absent `$schema`. A custom
# (unrecognized) profile resolves to an "unknown" version: gates accept a
# superset of v1 and v2.

V1_PROFILE = "https://datapackage.org/profiles/1.0/tableschema.json"
V2_PROFILE = "https://datapackage.org/profiles/2.0/tableschema.json"
CUSTOM_PROFILE = "https://example.com/profiles/custom-tableschema.json"

OBJECT_MISSING_VALUES = [{"value": "-99", "label": "REFUSED"}]
GATE_NOTE = "missing values in object form require datapackage v2"

MISSING_VALUES_VERSION_GATE_CASES = [
    (
        "v1-objects-rejected",
        V1_PROFILE,
        OBJECT_MISSING_VALUES,
        [["schema-error", GATE_NOTE]],
    ),
    ("v1-strings-valid", V1_PROFILE, ["", "NA"], []),
    ("v2-objects-valid", V2_PROFILE, OBJECT_MISSING_VALUES, []),
    ("custom-objects-valid", CUSTOM_PROFILE, OBJECT_MISSING_VALUES, []),
    # an absent `$schema` is an explicit v1
    (
        "no-schema-objects-rejected",
        None,
        OBJECT_MISSING_VALUES,
        [["schema-error", GATE_NOTE]],
    ),
]


@pytest.mark.parametrize(
    "name, schema, source, expected",
    MISSING_VALUES_VERSION_GATE_CASES,
    ids=[case[0] for case in MISSING_VALUES_VERSION_GATE_CASES],
)
def test_validate_missing_values_version_gate(name, schema, source, expected):
    descriptor = {
        "fields": [{"name": "name", "type": "string"}],
        "missingValues": source,
    }
    if schema is not None:
        descriptor["$schema"] = schema
    report = Schema.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == expected


# Exclusive bounds (version gate)
#
# `exclusiveMinimum`/`exclusiveMaximum` are a datapackage v2 addition,
# rejected under v1 — which is also the version of an absent `$schema`. A
# custom (unrecognized) profile resolves to an "unknown" version: gates
# accept a superset of v1 and v2.

EXCLUSIVE_BOUNDS = {"exclusiveMinimum": 1, "exclusiveMaximum": 10}
EXCLUSIVE_GATE_NOTES = [
    'constraint "exclusiveMinimum" requires datapackage v2',
    'constraint "exclusiveMaximum" requires datapackage v2',
]

EXCLUSIVE_BOUNDS_VERSION_GATE_CASES = [
    (
        "v1-rejected",
        V1_PROFILE,
        EXCLUSIVE_BOUNDS,
        [["field-error", note] for note in EXCLUSIVE_GATE_NOTES],
    ),
    ("v1-absent-valid", V1_PROFILE, {}, []),
    ("v2-valid", V2_PROFILE, EXCLUSIVE_BOUNDS, []),
    ("custom-profile-valid", CUSTOM_PROFILE, EXCLUSIVE_BOUNDS, []),
    # an absent `$schema` is an explicit v1
    (
        "no-schema-rejected",
        None,
        EXCLUSIVE_BOUNDS,
        [["field-error", note] for note in EXCLUSIVE_GATE_NOTES],
    ),
]


@pytest.mark.parametrize(
    "name, schema, constraints, expected",
    EXCLUSIVE_BOUNDS_VERSION_GATE_CASES,
    ids=[case[0] for case in EXCLUSIVE_BOUNDS_VERSION_GATE_CASES],
)
def test_validate_exclusive_bounds_version_gate(name, schema, constraints, expected):
    descriptor = {
        "fields": [{"name": "name", "type": "integer", "constraints": constraints}],
    }
    if schema is not None:
        descriptor["$schema"] = schema
    report = Schema.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == expected


# Integer `groupChar` (version gate)
#
# `groupChar` was already a property of number fields; integer fields only
# have it since datapackage v2, so it is rejected for them under v1 (which is
# also the version of an absent `$schema`).

GROUP_CHAR_GATE_NOTE = 'property "groupChar" of type "integer" requires datapackage v2'

INTEGER_GROUP_CHAR_VERSION_GATE_CASES = [
    (
        "v1-integer-rejected",
        V1_PROFILE,
        "integer",
        [["field-error", GROUP_CHAR_GATE_NOTE]],
    ),
    ("v1-number-valid", V1_PROFILE, "number", []),
    ("v2-integer-valid", V2_PROFILE, "integer", []),
    ("custom-profile-integer-valid", CUSTOM_PROFILE, "integer", []),
    (
        "no-schema-integer-rejected",
        None,
        "integer",
        [["field-error", GROUP_CHAR_GATE_NOTE]],
    ),
]


@pytest.mark.parametrize(
    "name, schema, type, expected",
    INTEGER_GROUP_CHAR_VERSION_GATE_CASES,
    ids=[case[0] for case in INTEGER_GROUP_CHAR_VERSION_GATE_CASES],
)
def test_validate_integer_group_char_version_gate(name, schema, type, expected):
    descriptor = {"fields": [{"name": "name", "type": type, "groupChar": ","}]}
    if schema is not None:
        descriptor["$schema"] = schema
    report = Schema.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == expected


# Missing values version gate — inheritance
#
# A `$schema` imposes its version on all descendants (top-down): a schema's
# version applies to its fields, and a field never declares its own `$schema`.

MISSING_VALUES_FIELD_INHERITS_SCHEMA_CASES = [
    ("v1-schema-rejects-field-objects", V1_PROFILE, [["field-error", GATE_NOTE]]),
    ("v2-schema-accepts-field-objects", V2_PROFILE, []),
    # an absent `$schema` is an explicit v1
    ("no-schema-rejects-field-objects", None, [["field-error", GATE_NOTE]]),
]


@pytest.mark.parametrize(
    "name, schema, expected",
    MISSING_VALUES_FIELD_INHERITS_SCHEMA_CASES,
    ids=[case[0] for case in MISSING_VALUES_FIELD_INHERITS_SCHEMA_CASES],
)
def test_validate_missing_values_version_gate_field_inherits_schema(
    name, schema, expected
):
    descriptor = {
        "fields": [
            {"name": "name", "type": "string", "missingValues": OBJECT_MISSING_VALUES}
        ]
    }
    if schema is not None:
        descriptor["$schema"] = schema
    report = Schema.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == expected


# Fields match


def test_validate_fields_match_unknown_value():
    report = Schema.validate_descriptor(
        {"fields": [{"name": "name", "type": "string"}], "fieldsMatch": "bogus"}
    )
    assert report.flatten(["type"]) == [["schema-error"]]


def test_validate_inline_set_default_field_type_if_missing():
    report = Schema.validate_descriptor(
        {"fields": [{"name": "name"}, {"name": "id", "type": "integer"}]}
    )
    assert report.flatten(["type", "note"]) == []


def test_validate_file_set_default_field_type_if_missing():
    report = Schema.validate_descriptor("data/invalid-schema.json")
    assert report.flatten(["type", "note"]) == []
