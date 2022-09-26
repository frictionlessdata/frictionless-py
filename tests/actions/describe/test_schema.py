from frictionless import Schema, describe


# General


def test_describe_schema():
    schema = describe("data/leading-zeros.csv", type="schema")
    assert isinstance(schema, Schema)
    assert schema.to_descriptor() == {"fields": [{"name": "value", "type": "string"}]}
