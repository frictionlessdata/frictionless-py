from frictionless import Dialect


def test_dialect_from_descriptor_v1():
    dialect = Dialect.from_descriptor({"delimiter": ";"})
    assert dialect.to_descriptor() == {"csv": {"delimiter": ";"}}
