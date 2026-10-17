from datetime import datetime

import pytest

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", 2000, 2000),
        ("default", "2000", 2000),
        ("default", -2000, None),
        ("default", 20000, None),
        ("default", "3.14", None),
        ("default", "", None),
    ],
)
def test_year_read_cell(format, source, target):
    field = Field.from_descriptor({"name": "name", "type": "year", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0000"),
        (1, "0001"),
        (12, "0012"),
        (123, "0123"),
        (999, "0999"),
        (1000, "1000"),
        (9999, "9999"),
    ],
)
def test_year_write_cell_roundtrip(value, expected):
    field = Field.from_descriptor({"name": "year", "type": "year"})
    assert field.read_cell(value) == (value, None)
    written, notes = field.write_cell(value)
    assert notes is None
    assert written == expected
    assert field.read_cell(written) == (value, None)


@pytest.mark.parametrize("year", [1, 12, 123, 999, 1000, 9999])
@pytest.mark.parametrize("type", ["date", "datetime", "yearmonth"])
def test_calendar_writer_four_digit_year(year, type):
    field = Field.from_descriptor({"name": "value", "type": type})
    value = datetime(year, 1, 2, 3, 4, 5)
    if type == "date":
        value = value.date()
    elif type == "yearmonth":
        value = field.read_cell((year, 1))[0]
    written, notes = field.write_cell(value)
    assert notes is None
    assert written.startswith(f"{year:04d}-01")
    assert field.read_cell(written) == (value, None)
