from frictionless import Resource


# General


def test_describe_resource():
    resource = Resource.describe("data/table.csv")
    assert resource.index() is None
