from frictionless import Dialect

# General


def test_describe_dialect():
    dialect = Dialect.describe("data/delimiter.csv")
    assert dialect.to_descriptor() == {"csv": {"delimiter": ";"}}
