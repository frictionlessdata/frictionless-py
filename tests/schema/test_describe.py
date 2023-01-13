from frictionless import Schema


# General


def test_describe_schema_issue_1232_1364():
    schema = Schema.describe("data/leading-zeros.csv")
    # The behaviour has been reverted in #1364 to follow Table Schema standard
    assert schema.to_descriptor() == {"fields": [{"name": "value", "type": "integer"}]}
