import pytest
from frictionless import Step


# General


def test_step_from_descriptor_type_framework_v4():
    with pytest.warns(UserWarning):
        step = Step.from_descriptor({"code": "table-print"})
        assert step.to_descriptor() == {"type": "table-print"}
