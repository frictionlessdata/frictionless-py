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
        {"fields": [{"name": "name", "type": "string"}], "missingValues": source}
    )
    assert report.flatten(["type", "note"]) == expected


def test_validate_field_missing_values_uniqueness():
    report = Schema.validate_descriptor(
        {
            "fields": [
                {
                    "name": "name",
                    "type": "string",
                    "missingValues": [
                        {"value": "-99", "label": "REFUSED"},
                        {"value": "-99", "label": "OMITTED"},
                    ],
                }
            ]
        }
    )
    assert report.flatten(["type", "note"]) == [
        ["field-error", 'missing value "-99" is not unique']
    ]


def test_validate_inline_set_default_field_type_if_missing():
    report = Schema.validate_descriptor(
        {"fields": [{"name": "name"}, {"name": "id", "type": "integer"}]}
    )
    assert report.flatten(["type", "note"]) == []


def test_validate_file_set_default_field_type_if_missing():
    report = Schema.validate_descriptor("data/invalid-schema.json")
    assert report.flatten(["type", "note"]) == []
