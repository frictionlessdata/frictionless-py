import pytest
from datetime import datetime, time
from dateutil.tz import tzoffset, tzutc
from frictionless import Resource, formats

pytestmark = pytest.mark.skip(reason="issue-1217")


# We don't use VCR for this module testing because
# HTTP requests can contain secrets from Google Credentials. Consider using:
# https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-sensitive-data-from-the-request


# Write


@pytest.mark.ci
def test_bigquery_parser_write(options):
    prefix = options.pop("prefix")
    service = options.pop("service")
    control = formats.BigqueryControl(table=prefix, **options)
    source = Resource("data/table.csv")
    target = source.write(service, control=control)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.ci
def test_bigquery_parser_write_timezone(options):
    prefix = options.pop("prefix")
    service = options.pop("service")
    control = formats.BigqueryControl(table=prefix, **options)
    source = Resource("data/timezone-with-id.csv")
    target = source.write(service, control=control)
    with target:
        assert target.read_rows() == [
            {
                "id": 1,
                "datetime": datetime(2020, 1, 1, 15),
                "time": time(15),
            },
            {
                "id": 2,
                "datetime": datetime(2020, 1, 1, 15, 0, tzinfo=tzutc()),
                "time": time(15, 0, tzinfo=tzutc()),
            },
            {
                "id": 3,
                "datetime": datetime(2020, 1, 1, 15, 0, tzinfo=tzoffset(None, 10800)),
                "time": time(15, 0, tzinfo=tzoffset(None, 10800)),
            },
            {
                "id": 4,
                "datetime": datetime(2020, 1, 1, 15, 0, tzinfo=tzoffset(None, -10800)),
                "time": time(15, 0, tzinfo=tzoffset(None, -10800)),
            },
        ]
