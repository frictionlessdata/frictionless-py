from frictionless import Schema, Field


def test_schema_metadata_bad_schema_format():
    schema = Schema(
        fields=[
            Field(
                name="name",
                type="boolean",
                format={"trueValues": "Yes", "falseValues": "No"},
            )
        ]
    )
    assert schema.metadata_valid is False
    assert schema.metadata_errors[0].code == "field-error"
