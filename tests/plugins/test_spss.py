import pytest
import datetime
from frictionless import Package, Resource, Table, FrictionlessException, helpers
from frictionless.plugins.spss import SpssStorage


# Parser


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for MacOS")
def test_spss_parser(tmpdir):
    target = str(tmpdir.join("table.sav"))

    # Write
    with Table("data/table.csv") as table:
        table.write(target)

    # Read
    with Table(target) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows(dict=True) == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.skip
@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for MacOS")
def test_spss_parser_write_timezone(tmpdir):
    target = str(tmpdir.join("table.sav"))
    with Table("data/timezone.csv") as table:
        table.write(target)
    with Table(target) as table:
        assert table.read_rows(dict=True) == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]


# Storage


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for MacOS")
def test_spss_storage_types(tmpdir):

    # Export/Import
    source = Package("data/storage/types.json")
    storage = source.to_spss(basepath=tmpdir, force=True)
    target = Package.from_spss(basepath=tmpdir)

    # Assert metadata
    assert target.get_resource("types").schema == {
        "fields": [
            {"name": "any", "type": "string"},  # type fallback
            {"name": "array", "type": "string"},  # type fallback
            {"name": "boolean", "type": "string"},  # type fallback
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
    assert target.get_resource("types").read_rows(dict=True) == [
        {
            "any": "中国人",
            "array": '["Mike", "John"]',
            "boolean": "true",
            "date": datetime.date(2015, 1, 1),
            "date_year": datetime.date(2015, 1, 1),
            "datetime": datetime.datetime(2015, 1, 1, 3, 0),
            "duration": "P1Y1M",
            "geojson": '{"type": "Point", "coordinates": [33, 33.33]}',
            "geopoint": "30,70",
            "integer": 1,
            "number": 7.0,
            "object": '{"chars": 560}',
            "string": "english",
            "time": datetime.time(3, 0),
            "year": 2015,
            "yearmonth": "2015-01",
        },
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for MacOS")
def test_spss_storage_integrity(tmpdir):

    # Export/Import
    source = Package("data/storage/integrity.json")
    storage = source.to_spss(basepath=tmpdir, force=True)
    target = Package.from_spss(basepath=tmpdir)

    # Assert metadata (main)
    assert target.get_resource("integrity_main").schema == {
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
    assert target.get_resource("integrity_link").schema == {
        "fields": [
            {"name": "main_id", "type": "integer"},
            {"name": "some_id", "type": "integer"},  # constraint removal
            {"name": "description", "type": "string"},  # constraint removal
        ],
        # primary key removal
        # foreign keys removal
    }

    # Assert data (main)
    assert target.get_resource("integrity_main").read_rows(dict=True) == [
        {"id": 1, "parent": None, "description": "english"},
        {"id": 2, "parent": 1, "description": "中国人"},
    ]

    # Assert data (link)
    assert target.get_resource("integrity_link").read_rows(dict=True) == [
        {"main_id": 1, "some_id": 1, "description": "note1"},
        {"main_id": 2, "some_id": 2, "description": "note2"},
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for MacOS")
def test_spss_storage_constraints(tmpdir):

    # Export/Import
    source = Package("data/storage/constraints.json")
    storage = source.to_spss(basepath=tmpdir, force=True)
    target = Package.from_spss(basepath=tmpdir)

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
    assert target.get_resource("constraints").read_rows(dict=True) == [
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


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for MacOS")
def test_spss_storage_read_resource_not_existent_error():
    storage = SpssStorage()
    with pytest.raises(FrictionlessException) as excinfo:
        storage.read_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for MacOS")
def test_spss_storage_write_resource_existent_error(tmpdir):
    resource = Resource(path="data/table.csv")
    storage = resource.to_spss(basepath=tmpdir)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.write_resource(resource)
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("already exists")
    # Cleanup storage
    storage.delete_package(list(storage))


@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for MacOS")
def test_spss_storage_delete_resource_not_existent_error():
    storage = SpssStorage()
    with pytest.raises(FrictionlessException) as excinfo:
        storage.delete_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")
