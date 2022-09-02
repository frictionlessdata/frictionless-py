import pytest
from frictionless import Check


# General


def test_check_from_descriptor_type_framework_v4():
    with pytest.warns(UserWarning):
        check = Check.from_descriptor({"code": "table-dimensions"})
        assert check.to_descriptor() == {"type": "table-dimensions"}
