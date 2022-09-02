import pytest
from dateutil.tz import tzoffset, tzutc
from datetime import datetime, date, time
from frictionless import Package, Resource, platform


pytestmark = pytest.mark.skipif(
    platform.type == "darwin" or platform.python == "3.10",
    reason="Not supported MacOS and Python3.10",
)


# General


def test_spss_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = source.write(str(tmpdir.join("table.sav")))
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_spss_parser_write_types(tmpdir):
    source = Package("data/storage/types.json").get_resource("types")
    target = source.write(str(tmpdir.join("table.sav")))
    with target:

        # Assert schema
        assert target.schema.to_descriptor() == {
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
                "date": date(2015, 1, 1),
                "date_year": date(2015, 1, 1),
                "datetime": datetime(2015, 1, 1, 3, 0),
                "duration": "P1Y1M",
                "geojson": '{"type": "Point", "coordinates": [33, 33.33]}',
                "geopoint": "30,70",
                "integer": 1,
                "number": 7.0,
                "object": '{"chars": 560}',
                "string": "english",
                "time": time(3, 0),
                "year": 2015,
                "yearmonth": "2015-01",
            },
        ]


def test_spss_storage_constraints(tmpdir):
    source = Package("data/storage/constraints.json").get_resource("constraints")
    target = source.write(str(tmpdir.join("table.sav")))
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


@pytest.mark.skip(reason="issue-1212")
def test_spss_parser_write_timezone(tmpdir):
    source = Resource("data/timezone.csv")
    target = source.write(str(tmpdir.join("table.sav")))
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
