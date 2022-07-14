from frictionless import Step


# General


def test_step_from_descriptor_type_v1x5():
    step = Step.from_descriptor({"code": "table-print"})
    assert step.to_descriptor() == {"type": "table-print"}
