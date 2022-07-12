from frictionless import Checklist, checks


# General


def test_checklist():
    checklist = Checklist(checks=[checks.ascii_value()], pick_errors=["type-error"])
    descriptor = checklist.to_descriptor()
    print(descriptor)
    assert descriptor == {
        "checks": [{"type": "ascii-value"}],
        "pickErrors": ["type-error"],
    }
