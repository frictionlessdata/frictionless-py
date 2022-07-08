import pytest
from frictionless import Resource, Dialect, Detector, helpers


# General


def test_describe_resource():
    resource = Resource.describe("data/table.csv")
    assert resource.metadata_valid
    assert resource.to_descriptor() == {
        "name": "table",
        "path": "data/table.csv",
        "type": "table",
        "scheme": "file",
        "format": "csv",
        "hashing": "md5",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "dialect": {"controls": [{"code": "local"}, {"code": "csv"}]},
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        },
    }


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_describe_resource_with_stats():
    resource = Resource.describe("data/table.csv", stats=True)
    assert resource.metadata_valid
    assert resource.to_descriptor() == {
        "name": "table",
        "path": "data/table.csv",
        "type": "table",
        "scheme": "file",
        "format": "csv",
        "hashing": "md5",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "dialect": {"controls": [{"code": "local"}, {"code": "csv"}]},
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        },
        "stats": {
            "hash": "6c2c61dd9b0e9c6876139a449ed87933",
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
    resource = Resource.describe("data/table-infer-boolean.xlsx")
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "number", "type": "integer"},
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


def test_describe_resource_values_with_leading_zeros_issue_492():
    resource = Resource.describe("data/leading-zeros.csv")
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "value", "type": "integer"},
        ]
    }
    assert resource.read_rows() == [{"value": 1}, {"value": 2}, {"value": 3}]


@pytest.mark.xfail(reason="Fix quote char detection")
def test_describe_schema_proper_quote_issue_493():
    resource = Resource.describe("data/issue-493.csv")
    assert resource.dialect.get_control("csv").quote_char == '"'
    assert len(resource.schema.fields) == 126


def test_describe_file_with_different_characters_name_issue_600():
    assert Resource.describe("data/table_with_data.csv").name == "table_with_data"
    assert Resource.describe("data/Table With Data.csv").name == "table-with-data"
    assert Resource.describe("data/Таблица.csv").name == "tablitsa"


def test_describe_resource_compression_gzip_issue_606():
    resource = Resource.describe("data/table.csv.gz", stats=True)
    assert resource.name == "table"
    assert resource.stats["hash"] == "edf56ce48e402d83eb08d5dac6aa2ad9"
    assert resource.stats["bytes"] == 61


@pytest.mark.xfail(reason="Decide on behaviour")
def test_describe_resource_with_json_format_issue_827():
    resource = Resource.describe("data/table.json")
    assert resource.name == "table"


def test_describe_resource_with_years_in_the_header_issue_825():
    resource = Resource.describe("data/issue-825.csv")
    assert resource.schema.field_names == ["Musei", "2011", "2010"]
