import pytest
from frictionless import describe, Resource, Package, formats, platform


# General


def test_describe():
    resource = describe("data/table.csv")
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
def test_describe_with_stats():
    resource = describe("data/table.csv", stats=True)
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


def test_describe_resource():
    resource = describe("data/table.csv")
    assert isinstance(resource, Resource)


def test_describe_package():
    resource = describe(["data/table.csv"])
    assert isinstance(resource, Package)


def test_describe_package_pattern():
    resource = describe("data/chunk*.csv")
    assert isinstance(resource, Package)


def test_describe_package_type_package():
    resource = describe("data/table.csv", type="package")
    assert isinstance(resource, Package)


# Bugs


def test_describe_blank_cells_issue_7():
    source = b"header1,header2\n1,\n2,\n3,\n"
    resource = describe(source, format="csv")
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "header1", "type": "integer"},
            {"name": "header2", "type": "any"},
        ]
    }


def test_describe_whitespace_cells_issue_7():
    source = b"header1,header2\n1, \n2, \n3, \n"
    resource = describe(source, format="csv")
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "header1", "type": "integer"},
            {"name": "header2", "type": "string"},
        ]
    }


def test_describe_whitespace_cells_with_skip_initial_space_issue_7():
    source = b"header1,header2\n1, \n2, \n3, \n"
    control = formats.CsvControl(skip_initial_space=True)
    resource = describe(source, format="csv", control=control)
    assert isinstance(resource, Resource)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "header1", "type": "integer"},
            {"name": "header2", "type": "any"},
        ]
    }


def test_describe_non_tabular_resource_issue_641():
    resource = describe("data/document.pdf", stats=True)
    assert resource.to_descriptor() == {
        "name": "document",
        "path": "data/document.pdf",
        "type": "file",
        "scheme": "file",
        "format": "pdf",
        "encoding": "utf-8",
        "mediatype": "application/pdf",
        "stats": {
            "md5": "3a503daaa773a3ea32b1fedd9fece844",
            "sha256": "8acf6c76fa7ad2e13531e8e41c93e944597db489aee53c8f1748e3aafaf165ef",
            "bytes": 262443,
        },
    }


def test_describe_non_tabular_html_issue_715():
    resource = describe("data/text.html")
    assert resource.to_descriptor() == {
        "type": "file",
        "name": "text",
        "path": "data/text.html",
        "scheme": "file",
        "format": "html",
        "encoding": "utf-8",
        "mediatype": "text/html",
    }
