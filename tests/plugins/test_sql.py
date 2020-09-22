import os
import pytest
import datetime
import sqlalchemy as sa
from frictionless import Table, Package, Resource, exceptions
from frictionless.plugins.sql import SqlDialect, SqlStorage
from dotenv import load_dotenv

load_dotenv(".env")


# Parser


def test_table_format_sql(database_url):
    dialect = SqlDialect(table="data")
    with Table(database_url, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_table_format_sql_order_by(database_url):
    dialect = SqlDialect(table="data", order_by="id")
    with Table(database_url, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_table_format_sql_order_by_desc(database_url):
    dialect = SqlDialect(table="data", order_by="id desc")
    with Table(database_url, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[2, "中国人"], [1, "english"]]


def test_table_format_sql_table_is_required_error(database_url):
    table = Table(database_url)
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "dialect-error"
    assert error.note.count("'table' is a required property")


def test_table_format_sql_headers_false(database_url):
    dialect = SqlDialect(table="data")
    with Table(database_url, dialect=dialect, headers=False) as table:
        assert table.header == []
        assert table.read_data() == [["id", "name"], [1, "english"], [2, "中国人"]]


def test_table_write_sqlite(database_url):
    source = "data/table.csv"
    dialect = SqlDialect(table="name", order_by="id")
    with Table(source) as table:
        table.write(database_url, dialect=dialect)
    with Table(database_url, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


# Storage


def test_storage_sqlite(database_url):
    engine = sa.create_engine(database_url)
    prefix = "prefix_"

    # Export/Import
    source = Package("data/package-storage.json")
    storage = source.to_sql(engine=engine, prefix=prefix, force=True)
    target = Package.from_sql(engine=engine, prefix=prefix)

    # Assert metadata

    assert target.get_resource("article").schema == {
        "fields": [
            {"name": "id", "type": "integer", "constraints": {"required": True}},
            {"name": "parent", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "current", "type": "boolean"},
            {"name": "rating", "type": "number"},
        ],
        "primaryKey": ["id"],
        "foreignKeys": [
            {"fields": "parent", "reference": {"resource": "", "fields": "id"}}
        ],
    }
    assert target.get_resource("comment").schema == {
        "fields": [
            {"name": "entry_id", "type": "integer", "constraints": {"required": True}},
            {"name": "user_id", "type": "integer", "constraints": {"required": True}},
            {"name": "comment", "type": "string"},
            {"name": "note", "type": "string"},  # type fallback
        ],
        "primaryKey": ["entry_id", "user_id"],
        "foreignKeys": [
            {"fields": "entry_id", "reference": {"resource": "article", "fields": "id"}}
        ],
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
def test_storage_postgresql():
    engine = sa.create_engine(os.environ["POSTGRESQL_URL"])
    prefix = "prefix_"

    # Export/Import
    source = Package("data/package-storage.json")
    storage = source.to_sql(engine=engine, prefix=prefix, force=True)
    target = Package.from_sql(engine=engine, prefix=prefix)

    # Assert metadata

    assert target.get_resource("article").schema == {
        "fields": [
            {"name": "id", "type": "integer", "constraints": {"required": True}},
            {"name": "parent", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "current", "type": "boolean"},
            {"name": "rating", "type": "number"},
        ],
        "primaryKey": ["id"],
        "foreignKeys": [
            {"fields": "parent", "reference": {"resource": "", "fields": "id"}}
        ],
    }
    assert target.get_resource("comment").schema == {
        "fields": [
            {"name": "entry_id", "type": "integer", "constraints": {"required": True}},
            {"name": "user_id", "type": "integer", "constraints": {"required": True}},
            {"name": "comment", "type": "string"},
            {"name": "note", "type": "string"},  # type fallback
        ],
        "primaryKey": ["entry_id", "user_id"],
        "foreignKeys": [
            {"fields": "entry_id", "reference": {"resource": "article", "fields": "id"}}
        ],
    }
    assert target.get_resource("location").schema == {
        "fields": [
            {"name": "geojson", "type": "object"},  # type downgrade
            {"name": "geopoint", "type": "string"},  # type fallback
        ]
    }
    assert target.get_resource("structure").schema == {
        "fields": [
            {"name": "object", "type": "object"},
            {"name": "array", "type": "object"},  # type downgrade
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
        {"geojson": {"type": "Point", "coordinates": [33, 33.33]}, "geopoint": "30,70"},
        {"geojson": {"type": "Point", "coordinates": [55, 55.55]}, "geopoint": "90,40"},
    ]
    # TOOD: fix array
    assert target.get_resource("structure").read_rows() == [
        {"object": {"chars": 560}, "array": None},
        {"object": {"chars": 970}, "array": None},
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
def test_storage_mysql():
    engine = sa.create_engine(os.environ["MYSQL_URL"])
    prefix = "prefix_"

    # Export/Import
    source = Package("data/package-storage.json")
    storage = source.to_sql(engine=engine, prefix=prefix, force=True)
    target = Package.from_sql(engine=engine, prefix=prefix)

    # Assert metadata

    assert target.get_resource("article").schema == {
        "fields": [
            {"name": "id", "type": "integer", "constraints": {"required": True}},
            {"name": "parent", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "current", "type": "integer"},  # type downgrade
            {"name": "rating", "type": "number"},
        ],
        "primaryKey": ["id"],
        "foreignKeys": [
            {"fields": "parent", "reference": {"resource": "", "fields": "id"}}
        ],
    }
    assert target.get_resource("comment").schema == {
        "fields": [
            {"name": "entry_id", "type": "integer", "constraints": {"required": True}},
            {"name": "user_id", "type": "integer", "constraints": {"required": True}},
            {"name": "comment", "type": "string"},
            {"name": "note", "type": "string"},  # type fallback
        ],
        "primaryKey": ["entry_id", "user_id"],
        "foreignKeys": [
            {"fields": "entry_id", "reference": {"resource": "article", "fields": "id"}}
        ],
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


def test_storage_read_resource_not_existent_error(database_url):
    engine = sa.create_engine(database_url)
    storage = SqlStorage(engine=engine)
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.read_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")


def test_storage_write_resource_existent_error(database_url):
    engine = sa.create_engine(database_url)
    resource = Resource(path="data/table.csv")
    storage = resource.to_sql(engine=engine)
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.write_resource(resource)
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("already exists")


def test_storage_delete_resource_not_existent_error(database_url):
    engine = sa.create_engine(database_url)
    storage = SqlStorage(engine=engine)
    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        storage.delete_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")


@pytest.mark.parametrize(
    "field, constraint",
    [
        ("id", {"minimum": 2}),
        ("id", {"maximum": 1}),
        ("name", {"minLength": 10}),
        ("name", {"maxLength": 1}),
        ("name", {"pattern": "bad"}),
        ("name", {"enum": ["bad"]}),
    ],
)
def test_storage_field_constraint_not_valid_error(database_url, field, constraint):
    engine = sa.create_engine(database_url)
    resource = Resource(path="data/table.csv")
    resource.infer()
    resource.schema.get_field(field).constraints = constraint
    with pytest.raises(sa.exc.IntegrityError):
        resource.to_sql(engine=engine)
