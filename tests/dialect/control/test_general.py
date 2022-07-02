from frictionless import Control


# General


def test_control():
    control = Control.from_descriptor({"code": "csv"})
    assert control.code == "csv"
