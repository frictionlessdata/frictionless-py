from frictionless import describe


# General


def test_describe_schema():
    schema = describe("data/leading-zeros.csv", type="schema")
    assert schema == {"fields": [{"name": "value", "type": "integer"}]}
