import pytest
from decimal import Decimal
from frictionless import Field


# Tests


@pytest.mark.parametrize(
    "format, source, target, options",
    [
        ("default", Decimal(1), Decimal(1), {}),
        ("default", 1, Decimal(1), {}),
        ("default", 1.0, Decimal(1), {}),
        ("default", 1 << 63, Decimal(1 << 63), {}),
        ("default", "1", Decimal(1), {}),
        ("default", "10.00", Decimal(10), {}),
        ("default", "10.50", Decimal(10.5), {}),
        ("default", 24.122667, Decimal("24.122667"), {}),
        ("default", "000835", Decimal("835"), {}),
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
    ],
)
def test_number_read_cell(format, source, target, options):
    descriptor = {"name": "name", "type": "number", "format": format}
    descriptor.update(options)
    field = Field(descriptor)
    cell, notes = field.read_cell(source)
    assert cell == target
