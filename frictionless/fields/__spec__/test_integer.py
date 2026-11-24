from decimal import Decimal

import pytest

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target, options",
    [
        ("default", 1, 1, {}),
        ("default", 1 << 63, 1 << 63, {}),
        ("default", "1", 1, {}),
        ("default", 1.0, 1, {}),
        ("default", "000835", 835, {}),
        ("default", "0", 0, {}),
        ("default", "00", 0, {}),
        ("default", "01", 1, {}),
        ("default", " 01 ", 1, {}),
        ("default", "0.0003", None, {}),
        ("default", "00", 0, {"bareNumber": False}),
        ("default", "01", 1, {"bareNumber": False}),
        ("default", Decimal("1.0"), 1, {}),
        ("default", "1$", 1, {"bareNumber": False}),
        ("default", "ab1$", 1, {"bareNumber": False}),
        ("default", "-12 €", -12, {"bareNumber": False}),
        ("default", "-12€", -12, {"bareNumber": False}),
        ("default", "€-12", -12, {"bareNumber": False}),
        ("default", "€ -12", -12, {"bareNumber": False}),
        ("default", True, None, {}),
        ("default", False, None, {}),
        ("default", 3.14, None, {}),
        ("default", "3.14", None, {}),
        ("default", Decimal("3.14"), None, {}),
        ("default", "", None, {}),
        ("default", "1,234", None, {}),
        ("default", "1,234", 1234, {"groupChar": ","}),
        ("default", "1,234,567", 1234567, {"groupChar": ","}),
        ("default", "-12 000", -12000, {"groupChar": " "}),
        ("default", "1.234", None, {"groupChar": ","}),
        ("default", "$1,234 USD", 1234, {"groupChar": ",", "bareNumber": False}),
    ],
)
def test_integer_read_cell(format, source, target, options):
    descriptor = {"name": "name", "type": "integer", "format": format}
    descriptor.update(options)
    field = Field.from_descriptor(descriptor)
    cell, notes = field.read_cell(source)
    assert cell == target


@pytest.mark.parametrize(
    "source, target, options",
    [
        (1234567, "1234567", {}),
        (1234567, "1,234,567", {"groupChar": ","}),
        (-12000, "-12 000", {"groupChar": " "}),
        (12, "12", {"groupChar": ","}),
    ],
)
def test_integer_write_cell_group_char(source, target, options):
    descriptor = {"name": "name", "type": "integer"}
    descriptor.update(options)
    field = Field.from_descriptor(descriptor)
    cell, notes = field.write_cell(source)
    assert cell == target
    assert notes is None
