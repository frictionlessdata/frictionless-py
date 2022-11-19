# type: ignore
import pytest
from datetime import datetime, time
from dateutil.tz import tzoffset, tzutc
from frictionless import Resource, formats

pytestmark = pytest.mark.skip(reason="issue-475")


# Write


@pytest.mark.vcr
def test_ckan_parser(options):
    url = options.pop("url")
    control = formats.CkanControl(resource="table", **options)
    source = Resource("data/table.csv")
    target = source.write(url, format="ckan", control=control)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_ckan_parser_timezone(options):
    url = options.pop("url")
    control = formats.CkanControl(resource="timezone", **options)
    source = Resource("data/timezone.csv")
    target = source.write(url, format="ckan", control=control)
    with target:
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
