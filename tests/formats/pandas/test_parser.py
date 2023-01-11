import pytz
import isodate
import pandas as pd
from decimal import Decimal
from dateutil.tz import tzoffset, tzutc
from datetime import datetime, time
from pandas.core.dtypes.common import is_datetime64_ns_dtype
from frictionless import Package, Resource, Schema, validate


# Read


def test_pandas_parser():
    dataframe = pd.DataFrame(data={"id": [1, 2], "name": ["english", "中国人"]})
    with Resource(dataframe) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_pandas_parser_from_dataframe_with_primary_key_having_datetime():
    df = pd.read_csv("data/vix.csv", sep=";", parse_dates=["Date"], index_col=["Date"])  # type: ignore
    with Resource(df) as resource:

        # Assert meta
        assert resource.schema.to_descriptor() == {
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


def test_pandas_parser_write():
    source = Resource("data/table.csv")
    target = source.write(format="pandas")
    assert target.data.to_dict("records") == [  # type: ignore
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_pandas_parser_nan_in_integer_resource_column():
    # see issue 1109
    res = Resource(
        [
            ["int", "number", "string"],
            ["1", "2.3", "string"],
            ["", "4.3", "string"],
            ["3", "3.14", "string"],
        ]
    )
    df = res.to_pandas()
    assert all(df.dtypes.values == pd.array([pd.Int64Dtype(), float, object]))  # type: ignore


def test_pandas_parser_nan_in_integer_csv_column():
    # see issue 1109
    res = Resource("data/issue-1109.csv")
    df = res.to_pandas()
    assert all(df.dtypes.values == pd.array([pd.Int64Dtype(), float, object]))  # type: ignore


def test_pandas_parser_write_types():
    source = Package("data/storage/types.json").get_resource("types")
    target = source.write(format="pandas")
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


def test_pandas_write_constraints():
    source = Package("data/storage/constraints.json").get_resource("constraints")
    target = source.write(format="pandas")
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


def test_pandas_parser_write_timezone():
    source = Resource("data/timezone.csv")
    target = source.write(format="pandas")
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


# Bugs


def test_pandas_parser_write_bug_1100():
    datapackage = Package("data/issue-1100.package.json")
    target = datapackage.resources[0].to_pandas()
    assert target.to_dict("records") == [  # type: ignore
        {"timestamp": pd.Timestamp(2022, 5, 25, 10, 39, 15)},
        {"timestamp": pd.Timestamp(2022, 5, 25, 10, 39, 15)},
    ]


def test_pandas_parser_write_bug_1105():
    datapackage = Package("data/issue-1105.package.json")
    target = datapackage.resources[0].to_pandas()
    assert target.to_dict() == {  # type: ignore
        "id": {
            pd.Timestamp("2020-01-01 12:00:00+0000", tz="UTC"): 1,
            pd.Timestamp("2020-01-01 15:00:00+0000", tz="UTC"): 0,
        }
    }


def test_pandas_parser_nan_with_field_type_information_1143():
    descriptor = {
        "dialect": {"delimiter": ","},
        "name": "issue-1109",
        "path": "data/issue-1109.csv",
        "schema": {
            "fields": [
                {"name": "int", "type": "integer"},
                {"name": "number", "type": "number"},
                {"name": "string", "type": "string"},
            ]
        },
    }
    res = Resource(descriptor)
    df = res.to_pandas()
    assert all(df.dtypes.values == pd.array([pd.Int64Dtype(), float, object]))  # type: ignore


def test_pandas_parser_nan_without_field_type_information_1143():
    descriptor = {
        "dialect": {"delimiter": ","},
        "name": "issue-1109",
        "path": "data/issue-1109.csv",
        "schema": {
            "fields": [
                {"name": "int", "type": "any"},
                {"name": "number", "type": "any"},
                {"name": "string", "type": "any"},
            ]
        },
    }
    res = Resource(descriptor)
    df = res.to_pandas()
    assert all(df.dtypes.values == pd.array([object, object, object]))  # type: ignore


def test_pandas_parser_preserve_datetime_field_type_1138():
    descriptor = {
        "name": "article",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "datetime", "type": "date"},
            ]
        },
        "data": [
            ["id", "datetime"],
            ["1", "2020-01-01 15:00:00"],
            ["2", "2020-01-01 15:00:00"],
        ],
    }
    resource = Resource(descriptor)
    df = resource.to_pandas()
    assert is_datetime64_ns_dtype(df.dtypes.values[1])  # type: ignore


def test_pandas_parser_test_issue_sample_data_1138():
    descriptor = {
        "path": "data/issue-1138.csv",
        "name": "pegeldaten-schleswig-holstein-114515",
        "profile": "tabular-data-resource",
        "format": "csv",
        "encoding": "iso8859-1",
        "dialect": {"delimiter": ";"},
        "schema": {
            "fields": [
                {"type": "date", "format": "%d.%m.%Y", "name": "Zeit [MEZ]"},
                {"type": "integer", "name": "Wasserstand"},
                {
                    "type": "string",
                    "name": "Status",
                    "constraints": {
                        "enum": ["qualitätsgesichert", "nicht qualitätsgesichert"]
                    },
                },
            ]
        },
    }
    resource = Resource(descriptor)
    df = resource.to_pandas()
    assert is_datetime64_ns_dtype(df.dtypes.values[0])  # type: ignore


def test_validate_package_with_in_code_resources_1245():
    datapackage = Package(name="package", basepath="")

    dataframe = pd.DataFrame(data={"id": [1, 2], "name": ["english", "中国人"]})

    schema = {
        "fields": [
            {"name": "id", "title": "ID", "type": "number"},
            {"name": "name", "title": "Name", "type": "string"},
        ]
    }
    resource = Resource(dataframe, name="resource", schema=Schema.from_descriptor(schema))

    datapackage.add_resource(resource)

    report = validate(datapackage)

    assert len(report.errors) == 0
