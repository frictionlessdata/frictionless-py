import pytz
import isodate
import datetime
import pandas as pd
from decimal import Decimal
from frictionless import Package, Resource


# Read


def test_pandas_parser():
    dataframe = pd.DataFrame(data={"id": [1, 2], "name": ["english", "中国人"]})
    with Resource(dataframe) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_pandas_parser_write():
    source = Resource("data/table.csv")
    target = source.write(format="pandas")
    assert target.data.to_dict("records") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_pandas_parser_write_types():
    source = Package("data/storage/types.json").get_resource("types")
    target = source.write(format="pandas")
    with target:

        # Assert schema
        assert target.schema == {
            "fields": [
                {"name": "any", "type": "string"},  # type fallback
                {"name": "array", "type": "array"},
                {"name": "boolean", "type": "boolean"},
                {"name": "date", "type": "date"},
                {"name": "date_year", "type": "date"},  # format removal
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
                "date": datetime.date(2015, 1, 1),
                "date_year": datetime.date(2015, 1, 1),
                "datetime": datetime.datetime(2015, 1, 1, 3, 0),
                "duration": isodate.parse_duration("P1Y1M"),
                "geojson": {"type": "Point", "coordinates": [33, 33.33]},
                "geopoint": [30, 70],
                "integer": 1,
                "number": 7,
                "object": {"chars": 560},
                "string": "english",
                "time": datetime.time(3, 0),
                "year": 2015,
                "yearmonth": [2015, 1],
            },
        ]


def test_pandas_write_constraints():
    source = Package("data/storage/constraints.json").get_resource("constraints")
    target = source.write(format="pandas")
    with target:

        # Assert schema
        assert target.schema == {
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


def test_pandas_parser_write_timezone():
    source = Resource("data/timezone.csv")
    target = source.write(format="pandas")
    with target:

        # Assert schema
        assert target.schema == {
            "fields": [
                {"name": "datetime", "type": "datetime"},
                {"name": "time", "type": "time"},
            ],
        }

        # Assert rows
        assert target.read_rows() == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]


def test_pandas_parser_from_dataframe_with_primary_key_having_datetime():
    df = pd.read_csv("data/vix.csv", sep=";", parse_dates=["Date"], index_col=["Date"])
    with Resource(df) as resource:

        # Assert meta
        assert resource.schema == {
            "fields": [
                {"name": "Date", "type": "datetime", "constraints": {"required": True}},
                {"name": "VIXClose", "type": "number"},
                {"name": "VIXHigh", "type": "number"},
                {"name": "VIXLow", "type": "number"},
                {"name": "VIXOpen", "type": "number"},
            ],
            "primaryKey": ["Date"],
        }

        # Assert rows
        assert resource.read_rows() == [
            {
                "Date": datetime.datetime(2004, 1, 5, tzinfo=pytz.utc),
                "VIXClose": Decimal("17.49"),
                "VIXHigh": Decimal("18.49"),
                "VIXLow": Decimal("17.44"),
                "VIXOpen": Decimal("18.45"),
            },
            {
                "Date": datetime.datetime(2004, 1, 6, tzinfo=pytz.utc),
                "VIXClose": Decimal("16.73"),
                "VIXHigh": Decimal("17.67"),
                "VIXLow": Decimal("16.19"),
                "VIXOpen": Decimal("17.66"),
            },
        ]
