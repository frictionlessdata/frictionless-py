import pytest
from frictionless import formats, Resource, Dialect, Detector, platform


# General


def test_describe_resource():
    resource = Resource.describe("data/table.csv")
    assert resource.to_descriptor() == {
        "name": "table",
        "path": "data/table.csv",
        "type": "table",
        "scheme": "file",
        "format": "csv",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        },
    }


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_describe_resource_with_stats():
    resource = Resource.describe("data/table.csv", stats=True)
    assert resource.to_descriptor() == {
        "name": "table",
        "path": "data/table.csv",
        "type": "table",
        "scheme": "file",
        "format": "csv",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        },
        "stats": {
            "md5": "6c2c61dd9b0e9c6876139a449ed87933",
            "sha256": "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
            "bytes": 30,
            "fields": 2,
            "rows": 2,
        },
    }


def test_describe_resource_schema():
    resource = Resource.describe("data/table-infer.csv")
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_describe_resource_schema_utf8():
    resource = Resource.describe("data/table-infer-utf8.csv")
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_describe_resource_schema_infer_volume():
    detector = Detector(sample_size=4)
    resource = Resource.describe("data/table-infer-row-limit.csv", detector=detector)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_describe_resource_schema_with_missing_values_default():
    resource = Resource.describe("data/table-infer-missing-values.csv")
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_describe_resource_schema_with_missing_values_using_the_argument():
    detector = Detector(field_missing_values=["-"])
    resource = Resource.describe("data/table-infer-missing-values.csv", detector=detector)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        "missingValues": ["-"],
    }


def test_describe_resource_schema_check_type_boolean_string_tie():
    dialect = Dialect(header=False)
    detector = Detector(field_names=["field"])
    resource = Resource.describe(
        [["f"], ["stringish"]], dialect=dialect, detector=detector
    )
    assert resource.schema.get_field("field").type == "string"


def test_describe_resource_schema_summary():
    resource = Resource.describe("data/countries.csv")
    resource.infer()
    output = resource.schema.to_summary()
    assert (
        output.count("| name        | type    | required   |")
        and output.count("| id          | integer |            |")
        and output.count("| neighbor_id | string  |            |")
        and output.count("| name        | string  |            |")
        and output.count("| population  | string  |            |")
    )


# Bugs


def test_describe_resource_schema_xlsx_file_with_boolean_column_issue_203():
    resource = Resource.describe(
        "data/table-infer-boolean.xlsx", control=formats.ExcelControl(stringified=True)
    )
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "number", "type": "number"},
            {"name": "string", "type": "string"},
            {"name": "boolean", "type": "boolean"},
        ],
    }


def test_describe_resource_schema_increase_limit_issue_212():
    detector = Detector(sample_size=200)
    resource = Resource.describe("data/table-infer-increase-limit.csv", detector=detector)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "a", "type": "integer"},
            {"name": "b", "type": "number"},
        ],
    }


def test_describe_resource_values_with_leading_zeros_issue_492_1232_1364():
    resource = Resource.describe("data/leading-zeros.csv")
    # The behaviour has been reverted in #1364 to follow Table Schema standard
    #  assert resource.schema.to_descriptor() == {
    #  "fields": [{"name": "value", "type": "string"}]
    #  }
    # assert resource.read_rows() == [{"value": "01"}, {"value": "002"}, {"value": "00003"}]
    assert resource.schema.to_descriptor() == {
        "fields": [{"name": "value", "type": "integer"}]
    }
    assert resource.read_rows() == [{"value": 1}, {"value": 2}, {"value": 3}]


def test_describe_file_with_different_characters_name_issue_600():
    assert Resource.describe("data/table_with_data.csv").name == "table_with_data"
    assert Resource.describe("data/Table With Data.csv").name == "table-with-data"
    assert Resource.describe("data/Таблица.csv").name == "tablitsa"


def test_describe_resource_compression_gzip_issue_606():
    resource = Resource.describe("data/table.csv.gz", stats=True)
    assert resource.name == "table"
    assert (
        resource.stats.sha256
        == "574bb747a97cf4352fb69398a8ed58e12143f6537c9eb19e85d289443e55b084"
    )
    assert resource.stats.bytes == 61


def test_describe_resource_with_json_format_issue_827():
    resource = Resource.describe(path="data/table.json")
    assert resource.name == "table"


def test_describe_resource_with_years_in_the_header_issue_825():
    resource = Resource.describe("data/issue-825.csv")
    assert resource.schema.field_names == ["Musei", "2011", "2010"]
