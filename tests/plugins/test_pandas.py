import pytest
import isodate
import datetime
from frictionless import Package, Resource, exceptions
from frictionless.plugins.pandas import PandasStorage

# Storage


def test_storage():

    # Export/Import
    source = Package("data/package-storage.json")
    storage = source.to_pandas()
    target = Package.from_pandas(dataframes=storage.dataframes)

    # Assert metadata

    assert target.get_resource("article").schema == {
        "fields": [
            {"name": "id", "type": "integer", "constraints": {"required": True}},
            {"name": "parent", "type": "number"},  # type downgrade
            {"name": "name", "type": "string"},
            {"name": "current", "type": "boolean"},
            {"name": "rating", "type": "number"},
        ],
        "primaryKey": ["id"],
        # foreign keys removal
    }
    assert target.get_resource("comment").schema == {
        "fields": [
            {"name": "entry_id", "type": "integer", "constraints": {"required": True}},
            {"name": "user_id", "type": "integer", "constraints": {"required": True}},
            {"name": "comment", "type": "string"},
            {"name": "note", "type": "string"},  # type fallback
        ],
        "primaryKey": ["entry_id", "user_id"],
        # foreign keys removal
    }
    assert target.get_resource("location").schema == {
        "fields": [
            {"name": "geojson", "type": "object"},
            {"name": "geopoint", "type": "array"},
        ]
    }
    assert target.get_resource("structure").schema == {
        "fields": [
            {"name": "object", "type": "object"},
            {"name": "array", "type": "array"},
        ]
    }
    assert target.get_resource("temporal").schema == {
        "fields": [
            {"name": "date", "type": "date"},
            {"name": "date_year", "type": "date"},  # format removal
            {"name": "datetime", "type": "datetime"},
            {"name": "duration", "type": "duration"},
            {"name": "time", "type": "time"},
            {"name": "year", "type": "integer"},  # type downgrade
            {"name": "yearmonth", "type": "array"},  # type downgrade
        ]
    }

    # Assert data

    assert target.get_resource("article").read_rows() == [
        {"id": 1, "parent": None, "name": "Taxes", "current": True, "rating": 9.5},
        {"id": 2, "parent": 1, "name": "中国人", "current": False, "rating": 7},
    ]
    assert target.get_resource("comment").read_rows() == [
        {"entry_id": 1, "user_id": 1, "comment": "good", "note": "note1"},
        {"entry_id": 2, "user_id": 2, "comment": "bad", "note": "note2"},
    ]
    assert target.get_resource("location").read_rows() == [
        {"geojson": {"type": "Point", "coordinates": [33, 33.33]}, "geopoint": [30, 70]},
        {"geojson": {"type": "Point", "coordinates": [55, 55.55]}, "geopoint": [90, 40]},
    ]
    assert target.get_resource("structure").read_rows() == [
        {"object": {"chars": 560}, "array": ["Mike", "John"]},
        {"object": {"chars": 970}, "array": ["Paul", "Alex"]},
    ]
    assert target.get_resource("temporal").read_rows() == [
        {
            "date": datetime.date(2015, 1, 1),
            "date_year": datetime.date(2015, 1, 1),
            "datetime": datetime.datetime(2015, 1, 1, 3, 0),
            "duration": isodate.parse_duration("P1Y1M"),
            "time": datetime.time(3, 0),
            "year": 2015,
            "yearmonth": [2015, 1],
        },
        {
            "date": datetime.date(2015, 12, 31),
            "date_year": datetime.date(2015, 1, 1),
            "datetime": datetime.datetime(2015, 12, 31, 15, 45, 33),
            "duration": isodate.parse_duration("P2Y2M"),
            "time": datetime.time(15, 45, 33),
            "year": 2015,
            "yearmonth": [2015, 1],
        },
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)


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
