from frictionless import list

# General


def test_describe_resource():
    resources = list("data/tables")
    assert resources[0].name == "chunk1"
    assert resources[1].name == "chunk2"
