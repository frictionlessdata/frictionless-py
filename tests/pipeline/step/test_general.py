from frictionless import Step


# General


def test_step():
    step = Step.from_descriptor({"type": "table-print"})
    assert step.type == "table-print"
