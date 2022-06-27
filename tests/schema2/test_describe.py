from frictionless import Schema2


# General


def test_describe_schema():
    schema = Schema2.describe("data/leading-zeros.csv")
    assert schema.to_descriptor() == {"fields": [{"name": "value", "type": "integer"}]}
