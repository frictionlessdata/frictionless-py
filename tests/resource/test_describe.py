import pytest

from frictionless import Detector, Dialect, Resource, formats, platform

# General


def test_resource_describe():
    resource = Resource.describe("data/table.csv")
    assert isinstance(resource, Resource)
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
def test_resource_describe_with_stats():
    resource = Resource.describe("data/table.csv", stats=True)
    assert isinstance(resource, Resource)
    assert resource.to_descriptor() == {
        "name": "table",
        "path": "data/table.csv",
        "type": "table",
        "scheme": "file",
        "format": "csv",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "hash": "sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
        "bytes": 30,
        "fields": 2,
        "rows": 2,
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        },
    }


def test_resource_describe_schema():
    resource = Resource.describe("data/table-infer.csv")
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_resource_describe_schema_utf8():
    resource = Resource.describe("data/table-infer-utf8.csv")
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_resource_describe_schema_infer_volume():
    detector = Detector(sample_size=4)
    resource = Resource.describe("data/table-infer-row-limit.csv", detector=detector)
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_resource_describe_schema_with_missing_values_default():
    resource = Resource.describe("data/table-infer-missing-values.csv")
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_resource_describe_schema_with_missing_values_using_the_argument():
    detector = Detector(field_missing_values=["-"])
    resource = Resource.describe("data/table-infer-missing-values.csv", detector=detector)
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        "missingValues": ["-"],
    }


def test_resource_describe_schema_check_type_boolean_string_tie():
    dialect = Dialect(header=False)
    detector = Detector(field_names=["field"])
    resource = Resource.describe(
        [["f"], ["stringish"]], dialect=dialect, detector=detector
    )
    assert isinstance(resource, Resource)
    assert resource.schema.get_field("field").type == "string"


def test_resource_describe_schema_summary():
    resource = Resource.describe("data/countries.csv")
    assert isinstance(resource, Resource)
    output = resource.schema.to_summary()
    assert (
        output.count("| name        | type    | required   |")
        and output.count("| id          | integer |            |")
        and output.count("| neighbor_id | string  |            |")
        and output.count("| name        | string  |            |")
        and output.count("| population  | string  |            |")
    )


# Bugs


def test_resource_describe_blank_cells_issue_7():
    source = b"header1,header2\n1,\n2,\n3,\n"
    resource = Resource.describe(source, format="csv")
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "header1", "type": "integer"},
            {"name": "header2", "type": "any"},
        ]
    }


def test_resource_describe_whitespace_cells_issue_7():
    source = b"header1,header2\n1, \n2, \n3, \n"
    resource = Resource.describe(source, format="csv")
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "header1", "type": "integer"},
            {"name": "header2", "type": "string"},
        ]
    }


def test_resource_describe_schema_xlsx_file_with_boolean_column_issue_203():
    resource = Resource.describe(
        "data/table-infer-boolean.xlsx", control=formats.ExcelControl(stringified=True)
    )
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "number", "type": "number"},
            {"name": "string", "type": "string"},
            {"name": "boolean", "type": "boolean"},
        ],
    }


def test_resource_describe_schema_increase_limit_issue_212():
    detector = Detector(sample_size=200)
    resource = Resource.describe("data/table-infer-increase-limit.csv", detector=detector)
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "a", "type": "integer"},
            {"name": "b", "type": "number"},
        ],
    }


def test_resource_describe_schema_proper_quote_issue_493():
    resource = Resource.describe("data/issue-493.csv")
    assert isinstance(resource, Resource)
    assert resource.dialect.to_descriptor() == {}
    assert len(resource.schema.fields) == 126


def test_resource_describe_file_with_different_characters_name_issue_600():
    assert Resource("data/table_with_data.csv").name == "table_with_data"
    assert Resource("data/Table With Data.csv").name == "table-with-data"
    assert Resource("data/Таблица.csv").name == "tablitsa"


def test_resource_describe_compression_gzip_issue_606():
    resource = Resource.describe("data/table.csv.gz", stats=True)
    assert isinstance(resource, Resource)
    assert resource.name == "table"
    assert (
        resource.stats.sha256
        == "574bb747a97cf4352fb69398a8ed58e12143f6537c9eb19e85d289443e55b084"
    )
    assert resource.stats.bytes == 61


def test_resource_describe_non_tabular_resource_issue_641():
    resource = Resource.describe("data/document.pdf", stats=True)
    assert resource.to_descriptor() == {
        "name": "document",
        "type": "file",
        "path": "data/document.pdf",
        "scheme": "file",
        "format": "pdf",
        "mediatype": "application/pdf",
        "hash": "sha256:8acf6c76fa7ad2e13531e8e41c93e944597db489aee53c8f1748e3aafaf165ef",
        "bytes": 262443,
        "encoding": "utf-8",
    }


def test_resource_describe_non_tabular_html_issue_715():
    resource = Resource.describe("data/text.html")
    assert resource.to_descriptor() == {
        "name": "text",
        "type": "text",
        "path": "data/text.html",
        "scheme": "file",
        "format": "html",
        "encoding": "utf-8",
        "mediatype": "text/html",
    }


def test_resource_describe_with_years_in_the_header_issue_825():
    resource = Resource.describe("data/issue-825.csv")
    assert isinstance(resource, Resource)
    assert resource.schema.field_names == ["Musei", "2011", "2010"]


def test_resource_describe_with_json_format_issue_827():
    resource = Resource.describe(path="data/table.json")
    assert isinstance(resource, Resource)
    assert resource.name == "table"
