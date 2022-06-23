import pytest
import datetime
from frictionless import Resource, Dialect
from frictionless.plugins.ckan import CkanControl


# General


@pytest.mark.skip
@pytest.mark.vcr
def test_ckan_parser(options):
    url = options.pop("url")
    dialect = Dialect(controls=[CkanControl(resource="table", **options)])
    source = Resource("data/table.csv")
    target = source.write(url, format="ckan", dialect=dialect)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# TODO: add timezone support or document if it's not possible
@pytest.mark.skip
@pytest.mark.vcr
def test_ckan_parser_timezone(options):
    url = options.pop("url")
    dialect = Dialect(controls=[CkanControl(resource="timezone", **options)])
    source = Resource("data/timezone.csv")
    target = source.write(url, format="ckan", dialect=dialect)
    with target:
        assert target.read_rows() == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]
