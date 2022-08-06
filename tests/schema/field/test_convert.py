from frictionless import Schema, Field


# General


def test_field_to_copy():
    source = Field.from_descriptor({"name": "name", "type": "integer"})
    target = source.to_copy()
    assert source is not target
    assert source == target


def test_field_set_schema():
    schema_prev = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    field = Field(schema=schema_prev)
    assert field.schema == schema_prev
    schema_next = Schema.from_descriptor({"fields": [{"name": "name", "type": "string"}]})
    field.schema = schema_next
    assert field.schema == schema_next
