import sys
import pytest
import datetime
from frictionless import Package, Resource, helpers


IS_MACOS = helpers.is_platform("macos")


# General


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="Not supported Python3.10")
def test_spss_parser_write(tmpdir):
    source = Resource("data/table.csv")
    if not IS_MACOS:
        target = source.write(str(tmpdir.join("table.sav")))
        with target:
            assert target.header == ["id", "name"]
            assert target.read_rows() == [
                {"id": 1, "name": "english"},
                {"id": 2, "name": "中国人"},
            ]


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="Not supported Python3.10")
def test_spss_parser_write_types(tmpdir):
    source = Package("data/storage/types.json").get_resource("types")
    if not IS_MACOS:
        target = source.write(str(tmpdir.join("table.sav")))
        with target:
            # Assert schema
            assert target.schema == {
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

            # Asssert rows
            assert target.read_rows() == [
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


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="Not supported Python3.10")
def test_spss_storage_constraints(tmpdir):
    source = Package("data/storage/constraints.json").get_resource("constraints")
    if not IS_MACOS:
        target = source.write(str(tmpdir.join("table.sav")))
        with target:
            # Assert schema
            assert target.schema == {
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

            # Asssert rows
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


# TODO: add timezone support or document if it's not possible
@pytest.mark.skipif(sys.version_info >= (3, 10), reason="Not supported Python3.10")
def test_spss_parser_write_timezone(tmpdir):
    source = Resource("data/timezone.csv")
    if not IS_MACOS:
        target = source.write(str(tmpdir.join("table.sav")))
        with target:
            # Assert schmea
            assert target.schema == {
                "fields": [
                    {"name": "datetime", "type": "datetime"},
                    {"name": "time", "type": "time"},
                ],
            }

            # Assert rows
            assert target.read_rows() == [
                {
                    "datetime": datetime.datetime(2020, 1, 1, 15),
                    "time": datetime.time(15),
                },
                {
                    "datetime": datetime.datetime(2020, 1, 1, 15),
                    "time": datetime.time(15),
                },
                {
                    "datetime": datetime.datetime(2020, 1, 1, 15),
                    "time": datetime.time(15),
                },
                {
                    "datetime": datetime.datetime(2020, 1, 1, 15),
                    "time": datetime.time(15),
                },
            ]
