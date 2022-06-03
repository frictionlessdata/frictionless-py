from frictionless import describe


# General


def test_describe_dialect():
    dialect = describe("data/delimiter.csv", type="dialect")
    assert dialect == {"delimiter": ";"}
