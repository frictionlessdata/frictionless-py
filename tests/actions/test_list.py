from frictionless import actions


# General


def test_describe_resource():
    resources = actions.list("data/tables")
    assert resources[0].name == "chunk1"
    assert resources[1].name == "chunk2"
