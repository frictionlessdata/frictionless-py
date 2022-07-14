import pytest
from frictionless import Check


# General


def test_step_from_descriptor_type_v1x5():
    with pytest.warns(UserWarning):
        check = Check.from_descriptor({"code": "table-dimensions"})
        assert check.to_descriptor() == {"type": "table-dimensions"}
