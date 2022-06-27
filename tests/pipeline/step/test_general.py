from frictionless import Step


# General


def test_step():
    step = Step.from_descriptor({"code": "table-print"})
    assert step.code == "table-print"
