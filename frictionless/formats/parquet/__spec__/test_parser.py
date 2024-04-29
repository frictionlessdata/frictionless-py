import datetime

import pytest

from frictionless import formats
from frictionless.resources import TableResource

# Read


def test_parquet_parser():
    with TableResource(path="data/table.parq") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_parquet_parser_parquet_extension():
    with TableResource(path="data/table.parquet") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_parquet_parser_columns():
    control = formats.ParquetControl(columns=["id"])
    with TableResource(path="data/table.parq", control=control) as resource:
        assert resource.header == ["id"]
        assert resource.read_rows() == [
            {"id": 1},
            {"id": 2},
        ]


@pytest.mark.ci
def test_parquet_parser_remote():
    with TableResource(
        path="https://raw.githubusercontent.com/fdtester/test-repo-with-parquet-data-file/main/table.parq"
    ) as resource:
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_parquet_parser_write(tmpdir):
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.parq")))
    source.write(target)
    with target:
        assert target.format == "parq"
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_parquet_parser_write_datetime_field_with_timezone(tmpdir):
    source = TableResource(data=[["datetimewithtimezone"], ["2025-08-24T15:20:10Z"]])
    target = TableResource(path=str(tmpdir.join("table.parq")))
    source.write(target)
    with target:
        assert target.format == "parq"
        assert target.header == ["datetimewithtimezone"]
        assert target.read_rows() == [
            {
                "datetimewithtimezone": datetime.datetime(
                    2025, 8, 24, 15, 20, 10, tzinfo=datetime.timezone.utc
                )
            }
        ]
