from datetime import datetime, time
from decimal import Decimal

import isodate
import polars as pl
import pytz
from dateutil.tz import tzoffset, tzutc

from frictionless import Package
from frictionless.resources import TableResource

# Read


def test_polars_parser():
    dataframe = pl.DataFrame(data={"id": [1, 2], "name": ["english", "中国人"]})
    with TableResource(data=dataframe) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_polars_parser_from_dataframe_with_datetime():
    # Polars does not have the concept of an index!
    df = pl.read_csv("data/vix.csv", separator=";", try_parse_dates=True)  # type: ignore
    with TableResource(data=df) as resource:
        # Assert meta
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "Date", "type": "datetime"},
                {"name": "VIXClose", "type": "number"},
                {"name": "VIXHigh", "type": "number"},
                {"name": "VIXLow", "type": "number"},
                {"name": "VIXOpen", "type": "number"},
            ]
        }
        rows = resource.read_rows()
        # Assert rows
        assert rows == [
            {
                "Date": datetime(2004, 1, 5, tzinfo=pytz.utc),
                "VIXClose": Decimal("17.49"),
                "VIXHigh": Decimal("18.49"),
                "VIXLow": Decimal("17.44"),
                "VIXOpen": Decimal("18.45"),
            },
            {
                "Date": datetime(2004, 1, 6, tzinfo=pytz.utc),
                "VIXClose": Decimal("16.73"),
                "VIXHigh": Decimal("17.67"),
                "VIXLow": Decimal("16.19"),
                "VIXOpen": Decimal("17.66"),
            },
        ]


# Write


def test_polars_parser_write():
    source = TableResource(path="data/table.csv")
    target = source.write(format="polars")
    assert target.data.to_dicts() == [  # type: ignore
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_polars_parser_nan_in_integer_resource_column():
    # see issue 1109
    res = TableResource(
        data=[
            ["int", "number", "string"],
            ["1", "2.3", "string"],
            ["", "4.3", "string"],
            ["3", "3.14", "string"],
        ]
    )
    df = res.to_polars()
    assert df.dtypes == [pl.Int64, pl.Float64, pl.String]  # type: ignore


def test_polars_parser_nan_in_integer_csv_column():
    res = TableResource(path="data/issue-1109.csv")
    df = res.to_polars()
    assert df.dtypes == [pl.Int64, pl.Float64, pl.String]  # type: ignore


def test_polars_parser_write_types():
    source = Package("data/storage/types.json").get_table_resource("types")
    target = source.write(format="polars")
    with target:
        # Assert schema
        assert target.schema.to_descriptor() == {
            "fields": [
                {"name": "any", "type": "string"},  # type fallback
                {"name": "array", "type": "array"},
                {"name": "boolean", "type": "boolean"},
                {"name": "date", "type": "datetime"},  # type downgrade
                {"name": "date_year", "type": "datetime"},  # type downgrade/fmt removal
                {"name": "datetime", "type": "datetime"},
                {"name": "duration", "type": "duration"},
                {"name": "geojson", "type": "object"},
                {"name": "geopoint", "type": "array"},
                {"name": "integer", "type": "integer"},
                {"name": "number", "type": "number"},
                {"name": "object", "type": "object"},
                {"name": "string", "type": "string"},
                {"name": "time", "type": "time"},
                {"name": "year", "type": "integer"},  # type downgrade
                {"name": "yearmonth", "type": "array"},  # type downgrade
            ],
        }

        # Assert rows
        assert target.read_rows() == [
            {
                "any": "中国人",
                "array": ["Mike", "John"],
                "boolean": True,
                "date": datetime(2015, 1, 1),
                "date_year": datetime(2015, 1, 1),
                "datetime": datetime(2015, 1, 1, 3, 0),
                "duration": isodate.parse_duration("P1Y1M"),
                "geojson": {"type": "Point", "coordinates": [33, 33.33]},
                "geopoint": [30, 70],
                "integer": 1,
                "number": 7,
                "object": {"chars": 560},
                "string": "english",
                "time": time(3, 0),
                "year": 2015,
                "yearmonth": [2015, 1],
            },
        ]


def test_polars_write_constraints():
    source = Package("data/storage/constraints.json").get_table_resource("constraints")
    target = source.write(format="polars")
    with target:
        # Assert schema
        assert target.schema.to_descriptor() == {
            "fields": [
                {"name": "required", "type": "string"},  # constraint removal
                {"name": "minLength", "type": "string"},  # constraint removal
                {"name": "maxLength", "type": "string"},  # constraint removal
                {"name": "pattern", "type": "string"},  # constraint removal
                {"name": "enum", "type": "string"},  # constraint removal
                {"name": "minimum", "type": "integer"},  # constraint removal
                {"name": "maximum", "type": "integer"},  # constraint removal
            ],
        }

        # Assert rows
        assert target.read_rows() == [
            {
                "required": "passing",
                "minLength": "passing",
                "maxLength": "passing",
                "pattern": "passing",
                "enum": "passing",
                "minimum": 5,
                "maximum": 5,
            },
        ]


def test_polars_parser_write_timezone():
    source = TableResource(path="data/timezone.csv")
    target = source.write(format="polars")
    with target:
        # Assert schema
        assert target.schema.to_descriptor() == {
            "fields": [
                {"name": "datetime", "type": "datetime"},
                {"name": "time", "type": "time"},
            ],
        }

        # Assert rows
        assert target.read_rows() == [
            {
                "datetime": datetime(2020, 1, 1, 15),
                "time": time(15),
            },
            {
                "datetime": datetime(2020, 1, 1, 15, 0, tzinfo=tzutc()),
                "time": time(15, 0, tzinfo=tzutc()),
            },
            {
                "datetime": datetime(2020, 1, 1, 15, 0, tzinfo=tzoffset(None, 10800)),
                "time": time(15, 0, tzinfo=tzoffset(None, 10800)),
            },
            {
                "datetime": datetime(2020, 1, 1, 15, 0, tzinfo=tzoffset(None, -10800)),
                "time": time(15, 0, tzinfo=tzoffset(None, -10800)),
            },
        ]
