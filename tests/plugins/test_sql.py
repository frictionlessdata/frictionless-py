import pytest
import datetime
import sqlalchemy as sa
from frictionless import Package, Resource, Layout, FrictionlessException
from frictionless.plugins.sql import SqlDialect, SqlStorage


# Parser


def test_sql_parser(database_url):
    dialect = SqlDialect(table="table")
    with Resource(database_url, dialect=dialect) as resource:
        assert resource.schema == {
            "fields": [
                {"name": "id", "type": "integer", "constraints": {"required": True}},
                {"name": "name", "type": "string"},
            ],
            "primaryKey": ["id"],
        }
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_order_by(database_url):
    dialect = SqlDialect(table="table", order_by="id")
    with Resource(database_url, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_order_by_desc(database_url):
    dialect = SqlDialect(table="table", order_by="id desc")
    with Resource(database_url, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 2, "name": "中国人"},
            {"id": 1, "name": "english"},
        ]


def test_sql_parser_where(database_url):
    dialect = SqlDialect(table="table", where="name = '中国人'")
    with Resource(database_url, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_table_is_required_error(database_url):
    resource = Resource(database_url)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "dialect-error"
    assert error.note.count("'table' is a required property")


# NOTE: Probably it's not correct behaviour
def test_sql_parser_headers_false(database_url):
    dialect = SqlDialect(table="table")
    layout = Layout(header=False)
    with Resource(database_url, dialect=dialect, layout=layout) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": None, "name": "name"},
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_write(database_url):
    source = Resource("data/table.csv")
    target = source.write(database_url, dialect=SqlDialect(table="name", order_by="id"))
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_write_where(database_url):
    source = Resource("data/table.csv")
    target = source.write(
        database_url, dialect=SqlDialect(table="name", where="name = '中国人'")
    )
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_write_timezone(sqlite_url):
    source = Resource("data/timezone.csv")
    target = source.write(sqlite_url, dialect=SqlDialect(table="timezone"))
    with target:
        assert target.header == ["datetime", "time"]
        assert target.read_rows() == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]


def test_sql_parser_write_timezone_postgresql(postgresql_url):
    source = Resource("data/timezone.csv")
    target = source.write(postgresql_url, dialect=SqlDialect(table="timezone"))
    with target:
        assert target.header == ["datetime", "time"]
        assert target.read_rows() == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]


def test_sql_parser_write_timezone_mysql(mysql_url):
    source = Resource("data/timezone.csv")
    target = source.write(mysql_url, dialect=SqlDialect(table="timezone"))
    with target:
        assert target.header == ["datetime", "time"]
        assert target.read_rows() == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]


def test_sql_parser_write_string_pk_issue_777_sqlite(sqlite_url):
    source = Resource("data/table.csv")
    source.infer()
    source.schema.primary_key = ["name"]
    target = source.write(sqlite_url, dialect=SqlDialect(table="name"))
    with target:
        assert target.schema.primary_key == ["name"]
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_write_string_pk_issue_777_postgresql(postgresql_url):
    source = Resource("data/table.csv")
    source.infer()
    source.schema.primary_key = ["name"]
    target = source.write(postgresql_url, dialect=SqlDialect(table="name"))
    with target:
        assert target.schema.primary_key == ["name"]
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_write_string_pk_issue_777_mysql(mysql_url):
    source = Resource("data/table.csv")
    source.infer()
    source.schema.primary_key = ["name"]
    source.schema.get_field("name").constraints["maxLength"] = 100
    target = source.write(mysql_url, dialect=SqlDialect(table="name"))
    with target:
        assert target.schema.primary_key == ["name"]
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# The resource.to_yaml call was failing before the fix (see the issue)
def test_sql_parser_describe_to_yaml_issue_821(database_url):
    dialect = SqlDialect(table="table")
    resource = Resource(database_url, dialect=dialect)
    resource.infer()
    assert resource.to_yaml()


# Storage (Sqlite)


def test_sql_storage_sqlite_types(sqlite_url):
    dialect = SqlDialect(prefix="prefix_")
    source = Package("data/storage/types.json")
    storage = source.to_sql(sqlite_url, dialect=dialect)
    target = Package.from_sql(sqlite_url, dialect=dialect)

    # Assert metadata
    assert target.get_resource("types").schema == {
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

    # Cleanup storage
    storage.delete_package(target.resource_names)


def test_sql_storage_sqlite_integrity(sqlite_url):
    dialect = SqlDialect(prefix="prefix_")
    source = Package("data/storage/integrity.json")
    storage = source.to_sql(sqlite_url, dialect=dialect)
    target = Package.from_sql(sqlite_url, dialect=dialect)

    # Assert metadata (main)
    assert target.get_resource("integrity_main").schema == {
        "fields": [
            {"name": "id", "type": "integer", "constraints": {"required": True}},
            {"name": "parent", "type": "integer"},
            {"name": "description", "type": "string"},
        ],
        "primaryKey": ["id"],
        "foreignKeys": [
            {"fields": ["parent"], "reference": {"resource": "", "fields": ["id"]}}
        ],
    }

    # Assert metadata (link)
    assert target.get_resource("integrity_link").schema == {
        "fields": [
            {"name": "main_id", "type": "integer", "constraints": {"required": True}},
            # removed unique
            {"name": "some_id", "type": "integer", "constraints": {"required": True}},
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

    # Cleanup storage
    storage.delete_package(target.resource_names)


def test_sql_storage_sqlite_constraints(sqlite_url):
    dialect = SqlDialect(prefix="prefix_")
    source = Package("data/storage/constraints.json")
    storage = source.to_sql(sqlite_url, dialect=dialect)
    target = Package.from_sql(sqlite_url, dialect=dialect)

    # Assert metadata
    assert target.get_resource("constraints").schema == {
        "fields": [
            {"name": "required", "type": "string", "constraints": {"required": True}},
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


@pytest.mark.parametrize(
    "field_name, cell",
    [
        ("required", ""),
        ("minLength", "bad"),
        ("maxLength", "badbadbad"),
        ("pattern", "bad"),
        # NOTE: It doesn't raise since sqlalchemy@1.4 (an underlaying bug?)
        # ("enum", "bad"),
        ("minimum", 3),
        ("maximum", 9),
    ],
)
def test_sql_storage_sqlite_constraints_not_valid_error(sqlite_url, field_name, cell):
    package = Package("data/storage/constraints.json")
    resource = package.get_resource("constraints")
    # We set an invalid cell to the data property
    for index, field in enumerate(resource.schema.fields):
        if field.name == field_name:
            resource.data[1][index] = cell
    # NOTE: should we wrap these exceptions?
    with pytest.raises(sa.exc.IntegrityError):
        resource.write(sqlite_url, dialect={"table": "table"})


def test_sql_storage_sqlite_read_resource_not_existent_error(sqlite_url):
    storage = SqlStorage(sqlite_url)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.read_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")


def test_sql_storage_sqlite_write_resource_existent_error(sqlite_url):
    storage = SqlStorage(sqlite_url)
    resource = Resource(path="data/table.csv")
    storage.write_resource(resource)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.write_resource(resource)
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("already exists")
    # Cleanup storage
    storage.delete_package(list(storage))


def test_sql_storage_sqlite_delete_resource_not_existent_error(sqlite_url):
    storage = SqlStorage(sqlite_url)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.delete_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")


def test_sql_storage_sqlite_views_support(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    engine.execute("CREATE TABLE 'table' (id INTEGER PRIMARY KEY, name TEXT)")
    engine.execute("INSERT INTO 'table' VALUES (1, 'english'), (2, '中国人')")
    engine.execute("CREATE VIEW 'table_view' AS SELECT * FROM 'table'")
    storage = SqlStorage(engine)
    resource = storage.read_resource("table_view")
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_sql_storage_sqlite_resource_url_argument(sqlite_url):
    source = Resource(path="data/table.csv")
    target = source.write(sqlite_url, dialect={"table": "table"})
    with target:
        assert target.schema == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_storage_sqlite_package_url_argument(sqlite_url):
    source = Package(resources=[Resource(path="data/table.csv")])
    source.to_sql(sqlite_url)
    target = Package.from_sql(sqlite_url)
    assert target.get_resource("table").schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_sql_storage_sqlite_integer_enum_issue_776(sqlite_url):
    dialect = SqlDialect(table="table")
    source = Resource(path="data/table.csv")
    source.infer()
    source.schema.get_field("id").constraints["enum"] = [1, 2]
    target = source.write(sqlite_url, dialect=dialect)
    assert target.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


# Storage (PostgreSQL)


def test_sql_storage_postgresql_types(postgresql_url):
    dialect = SqlDialect(prefix="prefix_")
    source = Package("data/storage/types.json")
    storage = source.to_sql(postgresql_url, dialect=dialect)
    target = Package.from_sql(postgresql_url, dialect=dialect)

    # Assert metadata
    assert target.get_resource("types").schema == {
        "fields": [
            {"name": "any", "type": "string"},  # type fallback
            {"name": "array", "type": "object"},  # type downgrade
            {"name": "boolean", "type": "boolean"},
            {"name": "date", "type": "date"},
            {"name": "date_year", "type": "date"},  # format removal
            {"name": "datetime", "type": "datetime"},
            {"name": "duration", "type": "string"},  # type fallback
            {"name": "geojson", "type": "object"},  # type downgrade
            {"name": "geopoint", "type": "string"},  # type fallback
            {"name": "integer", "type": "integer"},
            {"name": "number", "type": "number"},
            {"name": "object", "type": "object"},
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
            "array": None,  # NOTE: review why it's None
            "boolean": True,
            "date": datetime.date(2015, 1, 1),
            "date_year": datetime.date(2015, 1, 1),
            "datetime": datetime.datetime(2015, 1, 1, 3, 0),
            "duration": "P1Y1M",
            "geojson": {"type": "Point", "coordinates": [33, 33.33]},
            "geopoint": "30,70",
            "integer": 1,
            "number": 7,
            "object": {"chars": 560},
            "string": "english",
            "time": datetime.time(3, 0),
            "year": 2015,
            "yearmonth": "2015-01",
        },
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)


def test_sql_storage_postgresql_integrity(postgresql_url):
    dialect = SqlDialect(prefix="prefix_")
    source = Package("data/storage/integrity.json")
    storage = source.to_sql(postgresql_url, dialect=dialect)
    target = Package.from_sql(postgresql_url, dialect=dialect)

    # Assert metadata (main)
    assert target.get_resource("integrity_main").schema == {
        "fields": [
            # added required
            {"name": "id", "type": "integer", "constraints": {"required": True}},
            {"name": "parent", "type": "integer"},
            {"name": "description", "type": "string"},
        ],
        "primaryKey": ["id"],
        "foreignKeys": [
            {"fields": ["parent"], "reference": {"resource": "", "fields": ["id"]}}
        ],
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

    # Cleanup storage
    storage.delete_package(target.resource_names)


def test_sql_storage_postgresql_constraints(postgresql_url):
    dialect = SqlDialect(prefix="prefix_")
    source = Package("data/storage/constraints.json")
    storage = source.to_sql(postgresql_url, dialect=dialect)
    target = Package.from_sql(postgresql_url, dialect=dialect)

    # Assert metadata
    assert target.get_resource("constraints").schema == {
        "fields": [
            {"name": "required", "type": "string", "constraints": {"required": True}},
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


@pytest.mark.parametrize(
    "name, cell",
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
def test_sql_storage_postgresql_constraints_not_valid_error(postgresql_url, name, cell):
    package = Package("data/storage/constraints.json")
    resource = package.get_resource("constraints")
    # We set an invalid cell to the data property
    for index, field in enumerate(resource.schema.fields):
        if field.name == name:
            resource.data[1][index] = cell
    with pytest.raises((sa.exc.IntegrityError, sa.exc.DataError)):
        resource.write(postgresql_url, dialect={"table": "table"})


def test_sql_storage_postgresql_views_support(postgresql_url):
    engine = sa.create_engine(postgresql_url)
    engine.execute("DROP VIEW IF EXISTS data_view")
    engine.execute("DROP TABLE IF EXISTS data")
    engine.execute("CREATE TABLE data (id INTEGER PRIMARY KEY, name TEXT)")
    engine.execute("INSERT INTO data VALUES (1, 'english'), (2, '中国人')")
    engine.execute("CREATE VIEW data_view AS SELECT * FROM data")
    storage = SqlStorage(engine)
    resource = storage.read_resource("data_view")
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_sql_storage_postgresql_comment_support(postgresql_url):
    dialect = SqlDialect(table="table")

    # Write
    source = Resource(path="data/table.csv")
    source.infer()
    source.schema.get_field("id").description = "integer field"
    source.schema.get_field("name").description = "string field"
    source.write(postgresql_url, dialect=dialect)

    # Read
    target = Resource(postgresql_url, dialect=dialect)
    with target:
        assert target.schema == {
            "fields": [
                {"name": "id", "type": "integer", "description": "integer field"},
                {"name": "name", "type": "string", "description": "string field"},
            ]
        }
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Storage (MySQL)


def test_sql_storage_mysql_types(mysql_url):
    dialect = SqlDialect(prefix="prefix_")
    source = Package("data/storage/types.json")
    storage = source.to_sql(mysql_url, dialect=dialect)
    target = Package.from_sql(mysql_url, dialect=dialect)

    # Assert metadata
    assert target.get_resource("types").schema == {
        "fields": [
            {"name": "any", "type": "string"},  # type fallback
            {"name": "array", "type": "string"},  # type fallback
            {"name": "boolean", "type": "integer"},  # type downgrade
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

    # Cleanup storage
    storage.delete_package(target.resource_names)


def test_sql_storage_mysql_integrity(mysql_url):
    dialect = SqlDialect(prefix="prefix_")
    source = Package("data/storage/integrity.json")
    storage = source.to_sql(mysql_url, dialect=dialect)
    target = Package.from_sql(mysql_url, dialect=dialect)

    # Assert metadata (main)
    assert target.get_resource("integrity_main").schema == {
        "fields": [
            # added required
            {"name": "id", "type": "integer", "constraints": {"required": True}},
            {"name": "parent", "type": "integer"},
            {"name": "description", "type": "string"},
        ],
        "primaryKey": ["id"],
        "foreignKeys": [
            {"fields": ["parent"], "reference": {"resource": "", "fields": ["id"]}}
        ],
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

    # Cleanup storage
    storage.delete_package(target.resource_names)


def test_sql_storage_mysql_constraints(mysql_url):
    dialect = SqlDialect(prefix="prefix_")
    source = Package("data/storage/constraints.json")
    storage = source.to_sql(mysql_url, dialect=dialect)
    target = Package.from_sql(mysql_url, dialect=dialect)

    # Assert metadata
    assert target.get_resource("constraints").schema == {
        "fields": [
            {"name": "required", "type": "string", "constraints": {"required": True}},
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
def test_sql_storage_mysql_constraints_not_valid_error(mysql_url, field_name, cell):
    package = Package("data/storage/constraints.json")
    resource = package.get_resource("constraints")
    # We set an invalid cell to the data property
    for index, field in enumerate(resource.schema.fields):
        if field.name == field_name:
            resource.data[1][index] = cell
    # NOTE: should we wrap these exceptions? (why other exceptions for mysql here?)
    types = (sa.exc.IntegrityError, sa.exc.OperationalError, sa.exc.DataError)
    with pytest.raises(types):
        resource.write(mysql_url, dialect={"table": "table"})


def test_sql_storage_mysql_views_support(mysql_url):
    engine = sa.create_engine(mysql_url)
    engine.execute("DROP VIEW IF EXISTS data_view")
    engine.execute("DROP TABLE IF EXISTS data")
    engine.execute("CREATE TABLE data (id INTEGER PRIMARY KEY, name TEXT)")
    engine.execute("INSERT INTO data VALUES (1, 'english'), (2, '中国人')")
    engine.execute("CREATE VIEW data_view AS SELECT * FROM data")
    storage = SqlStorage(engine)
    resource = storage.read_resource("data_view")
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_sql_storage_mysql_comment_support(mysql_url):
    dialect = SqlDialect(table="table")

    # Write
    source = Resource(path="data/table.csv")
    source.infer()
    source.schema.get_field("id").description = "integer field"
    source.schema.get_field("name").description = "string field"
    source.write(mysql_url, dialect=dialect)

    # Read
    target = Resource(mysql_url, dialect=dialect)
    with target:
        assert target.schema == {
            "fields": [
                {"name": "id", "type": "integer", "description": "integer field"},
                {"name": "name", "type": "string", "description": "string field"},
            ]
        }
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
