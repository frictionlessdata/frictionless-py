from frictionless import Check


# General


def test_check():
    check = Check.from_descriptor({"code": "ascii-value"})
    assert check.code == "ascii-value"
