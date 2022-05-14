from frictionless import describe_dialect


# General


def test_describe_dialect():
    dialect = describe_dialect("data/delimiter.csv")
    assert dialect == {"delimiter": ";"}
