import sys

import pytest

from frictionless import Detector, Dialect, Schema
from frictionless.resources import TableResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_resource_stats_hash():
    with TableResource(path="data/doublequote.csv") as resource:
        resource.read_rows()
        assert (
            resource.stats.sha256
            == "41fdde1d8dbcb3b2d4a1410acd7ad842781f076076a73b049863d6c1c73868db"
        )


def test_resource_stats_hash_compressed():
    with TableResource(path="data/doublequote.csv.zip") as resource:
        resource.read_rows()
        assert (
            resource.stats.sha256
            == "88d0ef9887dcd7d7800bff2981f8cc496fbfcd8704a17c2aa12a434ce7d88b13"
        )


@pytest.mark.vcr
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
def test_resource_stats_hash_remote():
    with TableResource(path=BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert (
            resource.stats.sha256
            == "41fdde1d8dbcb3b2d4a1410acd7ad842781f076076a73b049863d6c1c73868db"
        )


def test_resource_stats_bytes():
    with TableResource(path="data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.bytes == 7346


def test_resource_stats_bytes_compressed():
    with TableResource(path="data/doublequote.csv.zip") as resource:
        resource.read_rows()
        assert resource.stats.bytes == 1265


@pytest.mark.vcr
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
def test_resource_stats_bytes_remote():
    with TableResource(path=BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.bytes == 7346


def test_resource_stats_fields():
    with TableResource(path="data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.fields == 17
        resource.open()
        resource.read_rows()
        assert resource.stats.fields == 17


@pytest.mark.parametrize("schema_sync", [True, False])
@pytest.mark.parametrize("field_names", [["id"], ["id", "name", "missing"]])
def test_resource_stats_fields_with_partial_schema(schema_sync, field_names):
    descriptor = {
        "fields": [
            {"name": name, "type": "string", "constraints": {"required": True}}
            for name in field_names
        ]
    }
    if not schema_sync:
        descriptor["fieldsMatch"] = "partial"
    resource = TableResource(
        data=[["id", "name"], ["1", "Alice"]],
        schema=Schema.from_descriptor(descriptor),
        detector=Detector(schema_sync=schema_sync),
    )

    report = resource.validate()

    assert report.tasks[0].stats["fields"] == 2
    assert resource.schema.field_names == field_names
    assert report.valid == ("missing" not in field_names)


def test_resource_stats_fields_without_header():
    with TableResource(data=[[1, 2]], dialect=Dialect(header=False)) as resource:
        resource.read_rows()
        assert resource.stats.fields == 2


@pytest.mark.vcr
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
def test_resource_stats_fields_remote():
    with TableResource(path=BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.fields == 17


def test_resource_stats_rows():
    with TableResource(path="data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.rows == 5
        resource.open()
        resource.read_rows()
        assert resource.stats.rows == 5


@pytest.mark.vcr
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
def test_resource_stats_rows_remote():
    with TableResource(path=BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.rows == 5


@pytest.mark.ci
def test_resource_stats_rows_significant():
    dialect = Dialect(header=False)
    with TableResource(path="data/table-1MB.csv", dialect=dialect) as resource:
        print(resource.read_rows())
        assert resource.stats.rows == 10000
