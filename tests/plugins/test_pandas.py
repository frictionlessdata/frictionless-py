import pytz
import pytest
import isodate
import datetime
import pandas as pd
from decimal import Decimal
from frictionless import Table, Package, Resource, exceptions
from frictionless.plugins.pandas import PandasStorage


# Parser


def test_table_pandas():
    dataframe = pd.DataFrame(data={"id": [1, 2], "name": ["english", "中国人"]})
    with Table(dataframe) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [
            [1, "english"],
            [2, "中国人"],
        ]


def test_table_pandas_write():
    with Table("data/table.csv") as table:
        dataframe = table.write(format="pandas")
        assert dataframe.to_dict("records") == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Storage


def test_storage_types():

    # Export/Import
    source = Package("data/storage/types.json")
    storage = source.to_pandas()
    target = Package.from_pandas(dataframes=storage.dataframes)

    # Assert metadata
    assert target.get_resource("types").schema == {
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

    # Assert data
    assert target.get_resource("types").read_rows() == [
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

    # Cleanup storage
    storage.delete_package(target.resource_names)


def test_storage_integrity():

    # Export/Import
    source = Package("data/storage/integrity.json")
    storage = source.to_pandas()
    target = Package.from_pandas(dataframes=storage.dataframes)

    # Assert metadata (main)
    assert target.get_resource("integrity_main").schema == {
        "fields": [
            # added required
            {"name": "id", "type": "integer", "constraints": {"required": True}},
            {"name": "parent", "type": "number"},  # type downgrade
            {"name": "description", "type": "string"},
        ],
        "primaryKey": ["id"],
        # foreign keys removal
    }

    # Assert metadata (link)
    assert target.get_resource("integrity_link").schema == {
        "fields": [
            # added required
            {"name": "main_id", "type": "integer", "constraints": {"required": True}},
            # added required; removed unique
            {"name": "some_id", "type": "integer", "constraints": {"required": True}},
            # removed unique
            {"name": "description", "type": "string"},
        ],
        "primaryKey": ["main_id", "some_id"],
        # foreign keys removal
    }

    # Assert data (main)
    assert target.get_resource("integrity_main").read_rows() == [
        {"id": 1, "parent": None, "description": "english"},
        {"id": 2, "parent": 1, "description": "中国人"},
    ]

    # Assert data (link)
    assert target.get_resource("integrity_link").read_rows() == [
        {"main_id": 1, "some_id": 1, "description": "note1"},
        {"main_id": 2, "some_id": 2, "description": "note2"},
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)


def test_storage_constraints():

    # Export/Import
    source = Package("data/storage/constraints.json")
    storage = source.to_pandas()
    target = Package.from_pandas(dataframes=storage.dataframes)

    # Assert metadata
    assert target.get_resource("constraints").schema == {
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

    # Assert data
    assert target.get_resource("constraints").read_rows() == [
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

    # Cleanup storage
    storage.delete_package(target.resource_names)


# NOTE: can we add constraints support to Pandas?
@pytest.mark.skip
@pytest.mark.parametrize(
    "field_name, cell",
    [
        ("required", ""),
        ("minLength", "bad"),
        ("maxLength", "badbadbad"),
        ("pattern", "bad"),
        ("enum", "bad"),
        ("minimum", 3),
        ("maximum", 9),
    ],
)
def test_storage_constraints_not_valid_error(field_name, cell):
    pass


def test_storage_read_resource_not_existent_error():
    storage = PandasStorage()
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.read_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")


def test_storage_write_resource_existent_error():
    resource = Resource(path="data/table.csv")
    storage = resource.to_pandas()
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.write_resource(resource)
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("already exists")
    # Cleanup storage
    storage.delete_package(list(storage))


def test_storage_delete_resource_not_existent_error():
    storage = PandasStorage()
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.delete_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")


def test_storage_dataframe_property_not_single_error():
    package = Package("data/package-storage.json")
    storage = package.to_pandas()
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.dataframe
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("single dataframe storages")


def test_storage_dataframe_primary_key_with_datetimes():
    df = pd.read_csv("data/vix.csv", sep=";", parse_dates=["Date"], index_col=["Date"])
    resource = Resource.from_pandas(df)
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
