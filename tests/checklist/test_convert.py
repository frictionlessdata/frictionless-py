from frictionless import Checklist, checks


# General


def test_checklist():
    checklist = Checklist(checks=[checks.ascii_value()], limit_errors=100)
    descriptor = checklist.to_descriptor()
    assert descriptor == {
        "checks": [{"code": "ascii-value"}],
        "limitErrors": 100,
    }
