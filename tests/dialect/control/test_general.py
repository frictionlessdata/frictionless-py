from frictionless import Control


# General


def test_dialect():
    control = Control.from_descriptor({"code": "csv"})
    assert control.code == "csv"
