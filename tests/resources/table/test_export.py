from frictionless.resources import TableResource

# General


def test_resource_to_view():
    resource = TableResource(path="data/table.csv")
    assert resource.to_view()
