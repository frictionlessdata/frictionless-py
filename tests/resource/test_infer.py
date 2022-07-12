import pytest
from frictionless import Resource, helpers


# General


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_resource_infer():
    resource = Resource(path="data/table.csv")
    resource.infer(stats=True)
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


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_resource_infer_source_non_tabular():
    resource = Resource(path="data/text.txt")
    resource.infer(stats=True)
    assert resource.metadata_valid
    assert resource.to_descriptor() == {
        "name": "text",
        "path": "data/text.txt",
        "type": "file",
        "scheme": "file",
        "format": "txt",
        "hashing": "md5",
        "encoding": "utf-8",
        # TODO: improve in detector.detect_resource
        "mediatype": "application/txt",
        "stats": {
            "hash": "e1cbb0c3879af8347246f12c559a86b5",
            "bytes": 5,
        },
    }


def test_resource_infer_from_path():
    resource = Resource("data/table.csv")
    resource.infer(stats=True)
    assert resource.metadata_valid
    assert resource.path == "data/table.csv"


# Bugs


def test_resource_infer_not_slugified_name_issue_531():
    resource = Resource("data/Table With Data.csv")
    resource.infer(stats=True)
    assert resource.metadata_valid
    assert resource.name == "table-with-data"
