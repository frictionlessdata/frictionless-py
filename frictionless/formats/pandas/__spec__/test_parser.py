from datetime import datetime, time, timedelta, timezone
from decimal import Decimal

import isodate
import numpy as np
import pandas as pd
import pytest
from dateutil.tz import tzoffset, tzutc
from pandas.api.types import is_datetime64_any_dtype

from frictionless import Package, Schema, validate
from frictionless.formats.pandas import PandasParser
from frictionless.resources import TableResource

# Infer dtype from real DataFrame as the type is depending on pandas' version
STRING_DTYPE = pd.DataFrame({"s": ["a"]}).dtypes["s"]

# Read


def test_pandas_parser():
    test_cases = [
        {
            "name": "Integer type only dataframe, cf issue 1678",
            "df_data": {"int": [1]},
            "expected_header": ["int"],
            "expected_rows": [{"int": 1}],
        },
        {
            "name": "Boolean type only dataframe, cf issue 1678",
            "df_data": {"bool": [True]},
            "expected_header": ["bool"],
            "expected_rows": [{"bool": True}],
        },
        {
            "name": "Mixed types dataframe, chinese characters",
            "df_data": {"id": [1, 2], "name": ["english", "中国人"]},
            "expected_header": ["id", "name"],
            "expected_rows": [
                {"id": 1, "name": "english"},
                {"id": 2, "name": "中国人"},
            ],
        },
    ]
    for tc in test_cases:
        dataframe = pd.DataFrame(data=tc["df_data"])

        with TableResource(data=dataframe) as resource:
            assert resource.header == tc["expected_header"], tc["name"]
            assert resource.read_rows() == tc["expected_rows"], tc["name"]


def test_pandas_parser_with_nan():
    dataframe = pd.DataFrame(data={"x": [np.nan]})

    with TableResource(data=dataframe) as resource:
        test_name = 'np.nan converted to Decimal("NaN")'
        row = resource.read_rows()[0]
        assert row["x"].is_nan(), test_name


def test_pandas_parser_from_dataframe_with_primary_key_having_datetime():
    df = pd.read_csv("data/vix.csv", sep=";", parse_dates=["Date"], index_col=["Date"])  # type: ignore
    with TableResource(data=df) as resource:
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
                "Date": datetime(2004, 1, 5, tzinfo=timezone.utc),
                "VIXClose": Decimal("17.49"),
                "VIXHigh": Decimal("18.49"),
                "VIXLow": Decimal("17.44"),
                "VIXOpen": Decimal("18.45"),
            },
            {
                "Date": datetime(2004, 1, 6, tzinfo=timezone.utc),
                "VIXClose": Decimal("16.73"),
                "VIXHigh": Decimal("17.67"),
                "VIXLow": Decimal("16.19"),
                "VIXOpen": Decimal("17.66"),
            },
        ]


@pytest.mark.parametrize("columns", [10, 94, 200])
@pytest.mark.parametrize("rows", [0, 3])
def test_pandas_parser_converts_each_row_once(mocker, rows, columns):
    dataframe = pd.DataFrame(
        {f"value_{column}": list(range(rows)) for column in range(columns)}, dtype="int64"
    )
    to_dict = mocker.spy(pd.Series, "to_dict")
    resource = TableResource(data=dataframe)

    cells = list(PandasParser(resource).read_cell_stream_create())

    assert cells == [list(dataframe.columns)] + [[row] * columns for row in range(rows)]
    assert to_dict.call_count == rows
    assert resource.schema.field_types == ["integer"] * columns


@pytest.mark.parametrize("tz", [None, timezone.utc, timezone(timedelta(hours=-5))])
def test_pandas_parser_mixed_values(tz):
    timestamp = datetime(2020, 1, 1, tzinfo=tz)
    dataframe = pd.DataFrame(
        {
            "integer": pd.Series([1, None], dtype="Int64"),
            "boolean": pd.Series([True, None], dtype="boolean"),
            "number": pd.Series([1.5, None], dtype="Float64"),
            "string": pd.Series(["中国人", None], dtype="string"),
            "datetime": pd.to_datetime([timestamp, None]),
            "object": pd.Series([{"key": "value"}, None], dtype=object),
            "array": pd.Series([[1, 2], None], dtype=object),
            "nan": pd.Series(["text", np.nan], dtype=object),
        }
    )
    resource = TableResource(data=dataframe)

    header, first, second = PandasParser(resource).read_cell_stream_create()

    assert header == list(dataframe.columns)
    assert first == [1, True, 1.5, "中国人", timestamp, {"key": "value"}, [1, 2], "text"]
    assert [type(value) for value in first[:3]] == [int, bool, float]
    assert type(first[4]) is datetime
    # pandas versions differ in whether to_dict boxes pd.NA as None.
    missing = pd.Series([pd.NA], dtype=object).to_dict()[0]
    assert all(value is missing for value in second[:4])
    assert second[4] is pd.NaT
    assert second[5:7] == [None, None]
    assert pd.isna(second[7])
    assert resource.schema.field_types == [
        "integer",
        "boolean",
        "number",
        "string",
        "datetime",
        "object",
        "array",
        "string",
    ]


@pytest.mark.parametrize("multiindex", [False, True])
def test_pandas_parser_index_and_declared_schema(multiindex):
    index = pd.Index([10, 20], name="id")
    primary_key = ["id"]
    index_fields = [{"name": "id", "type": "integer", "constraints": {"required": True}}]
    if multiindex:
        index = pd.MultiIndex.from_tuples([(10, "a"), (20, "b")], names=["id", "group"])
        primary_key.append("group")
        index_fields.append(
            {"name": "group", "type": "string", "constraints": {"required": True}}
        )
    dataframe = pd.DataFrame({"name": ["first", "second"], "value": [1, 2]}, index=index)
    inferred = TableResource(data=dataframe)
    inferred_cells = list(PandasParser(inferred).read_cell_stream_create())
    assert inferred_cells == [primary_key + ["name", "value"]] + (
        [[10, "a", "first", 1], [20, "b", "second", 2]]
        if multiindex
        else [[10, "first", 1], [20, "second", 2]]
    )
    assert inferred.schema.to_descriptor() == {
        "fields": index_fields
        + [
            {"name": "name", "type": "string"},
            {"name": "value", "type": "integer"},
        ],
        "primaryKey": primary_key,
    }
    # Declared schemas apply positionally, including names that differ from the frame.
    schema = Schema.from_descriptor(
        {
            "fields": index_fields
            + [
                {"name": "label", "type": "string"},
                {"name": "amount", "type": "integer", "constraints": {"minimum": 2}},
            ],
            "primaryKey": primary_key,
        }
    )
    resource = TableResource(data=dataframe, schema=schema)

    with resource:
        assert resource.header == primary_key + ["label", "amount"]
        rows = resource.read_rows()
        assert [list(row.values()) for row in rows] == (
            [[10, "a", "first", 1], [20, "b", "second", 2]]
            if multiindex
            else [[10, "first", 1], [20, "second", 2]]
        )
        assert resource.schema.to_descriptor() == schema.to_descriptor()

    report = resource.validate()
    assert not report.valid
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, len(primary_key) + 1, "incorrect-label"],
        [None, len(primary_key) + 2, "incorrect-label"],
        [2, len(primary_key) + 2, "constraint-error"],
    ]


def test_pandas_parser_index_only():
    dataframe = pd.DataFrame(index=pd.Index([10, 20], name="id"))
    resource = TableResource(data=dataframe)

    assert list(PandasParser(resource).read_cell_stream_create()) == [["id"], [10], [20]]
    assert resource.schema.primary_key == ["id"]


# Write


def test_pandas_parser_write():
    source = TableResource(path="data/table.csv")
    target = source.write(format="pandas")
    assert target.data.to_dict("records") == [  # type: ignore
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_pandas_parser_nan_in_integer_resource_column():
    # see issue 1109
    res = TableResource(
        data=[
            ["int", "number", "string"],
            ["1", "2.3", "string"],
            ["", "4.3", "string"],
            ["3", "3.14", "string"],
        ]
    )
    df = res.to_pandas()
    assert list(df.dtypes) == [pd.Int64Dtype(), np.dtype("float64"), STRING_DTYPE]


def test_pandas_parser_nan_in_integer_csv_column():
    # see issue 1109
    res = TableResource(path="data/issue-1109.csv")
    df = res.to_pandas()
    assert list(df.dtypes) == [pd.Int64Dtype(), np.dtype("float64"), STRING_DTYPE]


def test_pandas_parser_write_types():
    source = Package("data/storage/types.json").get_table_resource("types")
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
    source = Package("data/storage/constraints.json").get_table_resource("constraints")
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
    source = TableResource(path="data/timezone.csv")
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
    source = Package("data/issue-1100.package.json").get_table_resource("issue1100")
    target = source.to_pandas()
    assert target.to_dict("records") == [  # type: ignore
        {"timestamp": pd.Timestamp(2022, 5, 25, 10, 39, 15)},
        {"timestamp": pd.Timestamp(2022, 5, 25, 10, 39, 15)},
    ]


def test_pandas_parser_write_bug_1105():
    source = Package("data/issue-1105.package.json").get_table_resource("issue1105")
    target = source.to_pandas()
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
    res = TableResource.from_descriptor(descriptor)
    df = res.to_pandas()
    assert list(df.dtypes) == [pd.Int64Dtype(), np.dtype("float64"), STRING_DTYPE]


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
    res = TableResource.from_descriptor(descriptor)
    df = res.to_pandas()
    assert list(df.dtypes) == [STRING_DTYPE, STRING_DTYPE, STRING_DTYPE]


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
    resource = TableResource.from_descriptor(descriptor)
    df = resource.to_pandas()
    assert is_datetime64_any_dtype(df.dtypes.values[1])  # type: ignore


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
    resource = TableResource.from_descriptor(descriptor)
    df = resource.to_pandas()
    assert is_datetime64_any_dtype(df.dtypes.values[0])  # type: ignore


def test_validate_package_with_in_code_resources_1245():
    datapackage = Package(name="package", basepath="")
    dataframe = pd.DataFrame(data={"id": [1, 2], "name": ["english", "中国人"]})
    schema = {
        "fields": [
            {"name": "id", "title": "ID", "type": "number"},
            {"name": "name", "title": "Name", "type": "string"},
        ]
    }
    resource = TableResource(
        data=dataframe, name="resource", schema=Schema.from_descriptor(schema)
    )
    datapackage.add_resource(resource)
    report = validate(datapackage)
    assert len(report.errors) == 0
