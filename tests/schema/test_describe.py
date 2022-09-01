from frictionless import Schema


# General


def test_describe_schema():
    schema = Schema.describe("data/leading-zeros.csv")
    assert schema.to_descriptor() == {"fields": [{"name": "value", "type": "string"}]}
