import pytest
import datetime
from frictionless import Resource
from frictionless.plugins.bigquery import BigqueryDialect


# We don't use VCR for this module testing because
# HTTP requests can contain secrets from Google Credentials. Consider using:
# https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-sensitive-data-from-the-request


# General


@pytest.mark.ci
def test_bigquery_parser_write(options):
    prefix = options.pop("prefix")
    service = options.pop("service")
    dialect = BigqueryDialect(table=prefix, **options)
    source = Resource("data/table.csv")
    target = source.write(service, dialect=dialect)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# TODO: add timezone support or document if it's not possible
@pytest.mark.ci
def test_bigquery_parser_write_timezone(options):
    prefix = options.pop("prefix")
    service = options.pop("service")
    dialect = BigqueryDialect(table=prefix, **options)
    source = Resource("data/timezone.csv")
    target = source.write(service, dialect=dialect)
    with target:
        assert target.read_rows() == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]
