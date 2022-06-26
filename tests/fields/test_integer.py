import pytest
from decimal import Decimal
from frictionless import Field2


# General


@pytest.mark.parametrize(
    "format, source, target, options",
    [
        ("default", 1, 1, {}),
        ("default", 1 << 63, 1 << 63, {}),
        ("default", "1", 1, {}),
        ("default", 1.0, 1, {}),
        ("default", "000835", 835, {}),
        ("default", Decimal("1.0"), 1, {}),
        ("default", "1$", 1, {"bareNumber": False}),
        ("default", "ab1$", 1, {"bareNumber": False}),
        ("default", True, None, {}),
        ("default", False, None, {}),
        ("default", 3.14, None, {}),
        ("default", "3.14", None, {}),
        ("default", Decimal("3.14"), None, {}),
        ("default", "", None, {}),
    ],
)
def test_integer_read_cell(format, source, target, options):
    descriptor = {"name": "name", "type": "integer", "format": format}
    descriptor.update(options)
    field = Field2.from_descriptor(descriptor)
    cell, notes = field.read_cell(source)
    assert cell == target
