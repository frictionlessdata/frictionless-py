import io
import os
import json
import pytest
import datetime
from apiclient.discovery import build
from oauth2client.client import GoogleCredentials
from frictionless import Package, Resource, exceptions
from frictionless.plugins.bigquery import BigqueryStorage

# Storage


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".google.json"
credentials = GoogleCredentials.get_application_default()
OPTIONS = {
    "service": build("bigquery", "v2", credentials=credentials),
    "project": json.load(io.open(".google.json"))["project_id"],
    "dataset": "resource",
    "prefix": "prefix_",
}


@pytest.mark.ci
def test_storage():

    # Export/Import
    source = Package("data/package-storage.json")
    storage = source.to_bigquery(force=True, **OPTIONS)
    target = Package.from_bigquery(**OPTIONS)

    # Assert metadata

    assert target.get_resource("article").schema == {
        "fields": [
            {"name": "id", "type": "integer", "constraints": {"required": True}},
            {"name": "parent", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "current", "type": "boolean"},
            {"name": "rating", "type": "number"},
        ],
        # primary key removal
        # foreign keys removal
    }
    assert target.get_resource("comment").schema == {
        "fields": [
            {"name": "entry_id", "type": "integer", "constraints": {"required": True}},
            {"name": "user_id", "type": "integer", "constraints": {"required": True}},
            {"name": "comment", "type": "string"},
            {"name": "note", "type": "string"},  # type fallback
        ],
        # primary key removal
        # foreign keys removal
    }
    assert target.get_resource("location").schema == {
        "fields": [
            {"name": "geojson", "type": "string"},  # type fallback
            {"name": "geopoint", "type": "string"},  # type fallback
        ]
    }
    assert target.get_resource("structure").schema == {
        "fields": [
            {"name": "object", "type": "string"},  # type fallback
            {"name": "array", "type": "string"},  # type fallback
        ]
    }
    assert target.get_resource("temporal").schema == {
        "fields": [
            {"name": "date", "type": "date"},
            {"name": "date_year", "type": "date"},  # format removal
            {"name": "datetime", "type": "datetime"},
            {"name": "duration", "type": "string"},  # type fallback
            {"name": "time", "type": "time"},
            {"name": "year", "type": "integer"},  # type downgrade
            {"name": "yearmonth", "type": "string"},  # type fallback
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
        {"geojson": '{"type": "Point", "coordinates": [33, 33.33]}', "geopoint": "30,70"},
        {"geojson": '{"type": "Point", "coordinates": [55, 55.55]}', "geopoint": "90,40"},
    ]
    assert target.get_resource("structure").read_rows() == [
        {"object": '{"chars": 560}', "array": '["Mike", "John"]'},
        {"object": '{"chars": 970}', "array": '["Paul", "Alex"]'},
    ]
    assert target.get_resource("temporal").read_rows() == [
        {
            "date": datetime.date(2015, 1, 1),
            "date_year": datetime.date(2015, 1, 1),
            "datetime": datetime.datetime(2015, 1, 1, 3, 0),
            "duration": "P1Y1M",
            "time": datetime.time(3, 0),
            "year": 2015,
            "yearmonth": "2015-01",
        },
        {
            "date": datetime.date(2015, 12, 31),
            "date_year": datetime.date(2015, 1, 1),
            "datetime": datetime.datetime(2015, 12, 31, 15, 45, 33),
            "duration": "P2Y2M",
            "time": datetime.time(15, 45, 33),
            "year": 2015,
            "yearmonth": "2015-01",
        },
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)


@pytest.mark.ci
def test_storage_read_resource_not_existent_error():
    storage = BigqueryStorage(**OPTIONS)
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.read_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")


@pytest.mark.ci
def test_storage_write_resource_existent_error():
    resource = Resource(path="data/table.csv")
    storage = resource.to_bigquery(force=True, **OPTIONS)
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.write_resource(resource)
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("already exists")
    # Cleanup storage
    storage.delete_package(list(storage))


@pytest.mark.ci
def test_storage_delete_resource_not_existent_error():
    storage = BigqueryStorage(**OPTIONS)
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.delete_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")
