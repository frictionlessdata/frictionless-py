from frictionless import Schema, describe


# General


def test_describe_schema_issue_1232_1364():
    schema = describe("data/leading-zeros.csv", type="schema")
    assert isinstance(schema, Schema)
    # The behaviour has been reverted in #1364 to follow Table Schema standard
    #  assert schema.to_descriptor() == {"fields": [{"name": "value", "type": "string"}]}
    assert schema.to_descriptor() == {"fields": [{"name": "value", "type": "integer"}]}
