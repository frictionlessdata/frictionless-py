from frictionless import describe_schema


# General


def test_describe_schema():
    schema = describe_schema("data/leading-zeros.csv")
    assert schema == {"fields": [{"name": "value", "type": "integer"}]}
