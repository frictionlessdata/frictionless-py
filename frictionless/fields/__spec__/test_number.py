from decimal import Decimal

import pytest

from frictionless import Field, fields

# General


@pytest.mark.parametrize(
    "format, source, target, options",
    [
        ("default", Decimal(1), Decimal(1), {}),
        ("default", Decimal(1), 1, {"floatNumber": True}),
        ("default", 1, Decimal(1), {}),
        ("default", 1.0, Decimal(1), {}),
        ("default", 1.0, 1.0, {"floatNumber": True}),
        ("default", 1 << 63, Decimal(1 << 63), {}),
        ("default", "1", Decimal(1), {}),
        ("default", "10.00", Decimal(10), {}),
        ("default", "10.50", Decimal(10.5), {}),
        ("default", 24.122667, Decimal("24.122667"), {}),
        ("default", 24.122667, 24.122667, {"floatNumber": True}),
        ("default", "000835", 835, {}),
        ("default", "0", 0, {}),
        ("default", "00", 0, {}),
        ("default", "01", 1, {}),
        ("default", " 01 ", 1, {}),
        ("default", "0.003", Decimal("0.003"), {}),
        ("default", "-12.3 €", Decimal("-12.3"), {"bareNumber": False}),
        ("default", "-12.3€", Decimal("-12.3"), {"bareNumber": False}),
        ("default", "€-12.3", Decimal("-12.3"), {"bareNumber": False}),
        ("default", "€ -12.3", Decimal("-12.3"), {"bareNumber": False}),
        ("default", "100%", Decimal(100), {"bareNumber": False}),
        ("default", "1000‰", Decimal(1000), {"bareNumber": False}),
        ("default", "-1000", Decimal(-1000), {}),
        ("default", "1,000", Decimal(1000), {"groupChar": ","}),
        ("default", "10,000.00", Decimal(10000), {"groupChar": ","}),
        ("default", "10,000,000.50", Decimal(10000000.5), {"groupChar": ","}),
        ("default", "10#000.00", Decimal(10000), {"groupChar": "#"}),
        ("default", "10#000#000.50", Decimal(10000000.5), {"groupChar": "#"}),
        ("default", "10.50", Decimal(10.5), {"groupChar": "#"}),
        ("default", "1#000", Decimal(1000), {"groupChar": "#"}),
        ("default", "10#000@00", Decimal(10000), {"groupChar": "#", "decimalChar": "@"}),
        (
            "default",
            "10#000#000@50",
            Decimal(10000000.5),
            {"groupChar": "#", "decimalChar": "@"},
        ),
        ("default", "10@50", Decimal(10.5), {"groupChar": "#", "decimalChar": "@"}),
        ("default", "1#000", Decimal(1000), {"groupChar": "#", "decimalChar": "@"}),
        ("default", "10,000.00", Decimal(10000), {"groupChar": ",", "bareNumber": False}),
        (
            "default",
            "10,000,000.00",
            Decimal(10000000),
            {"groupChar": ",", "bareNumber": False},
        ),
        (
            "default",
            "10.000.000,00",
            Decimal(10000000),
            {"groupChar": ".", "decimalChar": ","},
        ),
        ("default", "$10000.00", Decimal(10000), {"bareNumber": False}),
        (
            "default",
            "  10,000.00 €",
            Decimal(10000),
            {"groupChar": ",", "bareNumber": False},
        ),
        ("default", "10 000,00", Decimal(10000), {"groupChar": " ", "decimalChar": ","}),
        (
            "default",
            "10 000 000,00",
            Decimal(10000000),
            {"groupChar": " ", "decimalChar": ","},
        ),
        (
            "default",
            "10000,00 ₪",
            Decimal(10000),
            {"groupChar": " ", "decimalChar": ",", "bareNumber": False},
        ),
        (
            "default",
            "  10 000,00 £",
            Decimal(10000),
            {"groupChar": " ", "decimalChar": ",", "bareNumber": False},
        ),
        ("default", True, None, {}),
        ("default", False, None, {}),
        ("default", "10,000a.00", None, {}),
        ("default", "10+000.00", None, {}),
        ("default", "$10:000.00", None, {}),
        ("default", "string", None, {}),
        ("default", "", None, {}),
        # Issue 1005
        ("default", "1.234", None, {"decimalChar": ","}),
        ("default", "1.234.", None, {"decimalChar": ",", "bareNumber": False}),
        ("default", "1234.", Decimal(1234), {"decimalChar": ",", "bareNumber": False}),
    ],
)
def test_number_read_cell(format, source, target, options):
    descriptor = {"name": "name", "type": "number", "format": format}
    descriptor.update(options)
    field = Field.from_descriptor(descriptor)
    cell = field.read_cell(source)[0]
    assert cell == target


# Bugs


def test_number_group_char_issue_1444():
    field = fields.NumberField(name="name", decimal_char=",", group_char=".")
    cell = field.read_cell("8.699,8")[0]
    assert cell == Decimal("8699.8")
    cell = field.write_cell(cell)[0]
    assert cell == "8.699,8"
