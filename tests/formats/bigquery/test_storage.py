import pytest
import datetime
from frictionless import Package, Resource, Dialect, formats
from frictionless import FrictionlessException

pytestmark = pytest.mark.skip(reason="issue-1217")


# We don't use VCR for this module testing because
# HTTP requests can contain secrets from Google Credentials. Consider using:
# https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-sensitive-data-from-the-request


# General


@pytest.mark.ci
def test_bigquery_storage_types(options):
    prefix = options.pop("prefix")
    service = options.pop("service")
    control = formats.BigqueryControl(table=prefix, **options)
    source = Package("data/storage/types.json")
    storage = source.to_bigquery(service, control=control)
    target = Package.from_bigquery(service, control=control)

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
            # converted into UTC
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


@pytest.mark.ci
def test_bigquery_storage_integrity(options):
    prefix = options.pop("prefix")
    service = options.pop("service")
    control = formats.BigqueryControl(table=prefix, **options)
    source = Package("data/storage/integrity.json")
    storage = source.to_bigquery(service, control=control)
    target = Package.from_bigquery(service, control=control)

    # Assert metadata (main)
    assert target.get_resource("integrity_main").schema.to_descriptor() == {
        "fields": [
            # added required
            {"name": "id", "type": "integer"},
            {"name": "parent", "type": "integer"},
            {"name": "description", "type": "string"},
        ],
        # primary key removal
        # foreign keys removal
    }

    # Assert metadata (link)
    assert target.get_resource("integrity_link").schema.to_descriptor() == {
        "fields": [
            {"name": "main_id", "type": "integer"},
            {"name": "some_id", "type": "integer"},  # constraint removal
            {"name": "description", "type": "string"},  # constraint removal
        ],
        # primary key removal
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


@pytest.mark.ci
def test_bigquery_storage_constraints(options):
    prefix = options.pop("prefix")
    service = options.pop("service")
    control = formats.BigqueryControl(table=prefix, **options)
    source = Package("data/storage/constraints.json")
    storage = source.to_bigquery(service, control=control)
    target = Package.from_bigquery(service, control=control)

    # Assert metadata
    assert target.get_resource("constraints").schema.to_descriptor() == {
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


@pytest.mark.ci
def test_bigquery_storage_read_resource_not_existent_error(options):
    service = options.pop("service")
    control = formats.BigqueryControl(**options)
    storage = formats.BigqueryStorage(service, control=control)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.read_resource("bad")
    error = excinfo.value.error
    assert error.type == "error"
    assert error.note.count("does not exist")


@pytest.mark.ci
def test_bigquery_storage_write_resource_existent_error(options):
    service = options.pop("service")
    control = formats.BigqueryControl(**options)
    storage = formats.BigqueryStorage(service, control=control)
    resource = Resource(path="data/table.csv")
    storage.write_resource(resource, force=True)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.write_resource(resource)
    error = excinfo.value.error
    assert error.type == "error"
    assert error.note.count("already exists")
    # Cleanup storage
    storage.delete_package(list(storage))


@pytest.mark.ci
def test_bigquery_storage_delete_resource_not_existent_error(options):
    service = options.pop("service")
    control = formats.BigqueryControl(**options)
    storage = formats.BigqueryStorage(service, control=control)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.delete_resource("bad")
    error = excinfo.value.error
    assert error.type == "error"
    assert error.note.count("does not exist")


@pytest.mark.ci
def test_storage_big_file(options):
    service = options.pop("service")
    control = formats.BigqueryControl(**options)
    storage = formats.BigqueryStorage(service, control=control)
    resource = Resource(name="table", data=[[1]] * 1500, dialect=Dialect(header=False))
    storage.write_resource(resource, force=True)
    target = storage.read_resource("table")
    assert len(target.read_rows()) == 1500
    storage.delete_package(list(storage))
