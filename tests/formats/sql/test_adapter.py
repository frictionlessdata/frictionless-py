import pytest
import datetime
from frictionless import Package


# Read


def test_sql_adapter_read_package(database_url):
    package = Package(database_url)
    assert len(package.resources) == 2


# Write


def test_sql_adapter_write_package_types(sqlite_url):
    source = Package("data/storage/types.json")
    source.publish(sqlite_url)
    target = Package(sqlite_url)

    # Assert metadata
    assert target.get_resource("types").schema.to_descriptor() == {
        "fields": [
            {"name": "any", "type": "string"},  # type fallback
            {"name": "array", "type": "string"},  # type fallback
            {"name": "boolean", "type": "boolean"},
            {"name": "date", "type": "date"},
            {"name": "date_year", "type": "date"},  # format removal
            {"name": "datetime", "type": "datetime"},
            {"name": "duration", "type": "string"},  # type fallback
            {"name": "geojson", "type": "string"},  # type fallback
            {"name": "geopoint", "type": "string"},  # type fallback
            {"name": "integer", "type": "integer"},
            {"name": "number", "type": "number"},
            {"name": "object", "type": "string"},  # type fallback
            {"name": "string", "type": "string"},
            {"name": "time", "type": "time"},
            {"name": "year", "type": "integer"},  # type downgrade
            {"name": "yearmonth", "type": "string"},  # type fallback
        ],
    }

    # Assert data
    assert target.get_resource("types").read_rows() == [
        {
            "any": "中国人",
            "array": '["Mike", "John"]',
            "boolean": True,
            "date": datetime.date(2015, 1, 1),
            "date_year": datetime.date(2015, 1, 1),
            "datetime": datetime.datetime(2015, 1, 1, 3, 0),
            "duration": "P1Y1M",
            "geojson": '{"type": "Point", "coordinates": [33, 33.33]}',
            "geopoint": "30,70",
            "integer": 1,
            "number": 7,
            "object": '{"chars": 560}',
            "string": "english",
            "time": datetime.time(3, 0),
            "year": 2015,
            "yearmonth": "2015-01",
        },
    ]


def test_sql_adapter_write_package_integrity(sqlite_url):
    source = Package("data/storage/integrity.json")
    source.publish(sqlite_url)
    target = Package(sqlite_url)

    # Assert metadata (main)
    assert target.get_resource("integrity_main").schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "parent", "type": "integer"},
            {"name": "description", "type": "string"},
        ],
        "primaryKey": ["id"],
        "foreignKeys": [
            {"fields": ["parent"], "reference": {"resource": "", "fields": ["id"]}}
        ],
    }

    # Assert metadata (link)
    assert target.get_resource("integrity_link").schema.to_descriptor() == {
        "fields": [
            {"name": "main_id", "type": "integer"},
            # removed unique
            {"name": "some_id", "type": "integer"},
            # removed unique
            {"name": "description", "type": "string"},
        ],
        "primaryKey": ["main_id", "some_id"],
        "foreignKeys": [
            {
                "fields": ["main_id"],
                "reference": {"resource": "integrity_main", "fields": ["id"]},
            }
        ],
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
