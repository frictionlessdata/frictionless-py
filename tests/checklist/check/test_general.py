from frictionless import Check


# General


def test_check():
    check = Check.from_descriptor({"type": "ascii-value"})
    assert check.type == "ascii-value"
