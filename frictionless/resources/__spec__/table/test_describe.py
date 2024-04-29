from frictionless import Resource
from frictionless.resources import TableResource

# Bugs


def test_resource_describe_values_with_leading_zeros_issue_492_1232_1364():
    resource = Resource.describe("data/leading-zeros.csv")
    # The behaviour has been reverted in #1364 to follow Table Schema standard
    #  assert resource.schema.to_descriptor() == {
    #  "fields": [{"name": "value", "type": "string"}]
    #  }
    # assert resource.read_rows() == [{"value": "01"}, {"value": "002"}, {"value": "00003"}]
    assert isinstance(resource, TableResource)
    assert resource.schema.to_descriptor() == {
        "fields": [{"name": "value", "type": "integer"}]
    }
    assert resource.read_rows() == [{"value": 1}, {"value": 2}, {"value": 3}]
