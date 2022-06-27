from frictionless import Schema, Field


# General


def test_field_to_copy():
    source = Field.from_descriptor({"type": "integer"})
    target = source.to_copy()
    assert source is not target
    assert source == target


def test_field_set_schema():
    test_schema_init = Schema(
        fields=[
            Field.from_descriptor(
                {
                    "name": "name",
                    "type": "boolean",
                    "format": {"trueValues": "Yes", "falseValues": "No"},
                }
            )
        ]
    )
    field = Field(schema=test_schema_init)
    assert field.schema == test_schema_init
    test_schema_property = Schema.from_descriptor(
        {"fields": [{"name": "name", "type": "other"}]}
    )
    field.schema = test_schema_property
    assert field.schema == test_schema_property
