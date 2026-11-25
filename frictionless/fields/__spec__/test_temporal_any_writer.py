from datetime import date, datetime, time, timedelta, timezone

import pytest

from frictionless import Field


@pytest.mark.parametrize(
    "type, value",
    [
        ("date", date(2026, 10, 14)),
        ("date", date(1, 1, 2)),
        ("datetime", datetime(2026, 10, 14, 6, 30, 15, 123456)),
        ("datetime", datetime(2026, 10, 14, 6, 30, tzinfo=timezone.utc)),
        ("datetime", datetime(1, 1, 2, 6, 30, tzinfo=timezone(timedelta(hours=1)))),
        ("time", time(6, 30, 15, 123456)),
        ("time", time(6, 30, tzinfo=timezone.utc)),
        ("time", time(6, 30, tzinfo=timezone(timedelta(hours=1)))),
    ],
)
def test_any_temporal_format_writes_readable_values(type, value):
    field = Field.from_descriptor({"name": "value", "type": type, "format": "any"})
    written, notes = field.write_cell(value)
    assert notes is None
    assert written != "any"
    assert field.read_cell(written) == (value, None)


@pytest.mark.parametrize(
    "type, value",
    [
        (
            "datetime",
            datetime(2026, 10, 14, 6, 30, tzinfo=timezone(timedelta(seconds=30))),
        ),
        ("time", time(6, 30, tzinfo=timezone(timedelta(seconds=30)))),
    ],
)
def test_any_temporal_format_preserves_offset_seconds(type, value):
    field = Field.from_descriptor({"name": "value", "type": type, "format": "any"})
    assert field.write_cell(value) == (value.isoformat(), None)


@pytest.mark.parametrize(
    "type, value, format",
    [
        ("date", date(2026, 10, 14), "%d/%m/%Y"),
        ("datetime", datetime(2026, 10, 14, 6, 30, 15, 123456), "%d/%m/%Y %H:%M:%S"),
        ("time", time(6, 30, 15, 123456), "%H:%M:%S"),
    ],
)
def test_custom_temporal_format_is_preserved(type, value, format):
    field = Field.from_descriptor({"name": "value", "type": type, "format": format})
    assert field.write_cell(value) == (value.strftime(format), None)
