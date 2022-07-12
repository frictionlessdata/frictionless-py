from frictionless import Control


# General


def test_control():
    control = Control.from_descriptor({"type": "csv"})
    assert control.type == "csv"
