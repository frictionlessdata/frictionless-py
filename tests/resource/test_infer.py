import pytest
from frictionless import Resource, platform


# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_infer():
    resource = Resource(path="data/table.csv")
    resource.infer(stats=True)
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


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_infer_source_non_tabular():
    resource = Resource(path="data/text.txt")
    resource.infer(stats=True)
    assert resource.to_descriptor() == {
        "name": "text",
        "path": "data/text.txt",
        "type": "file",
        "scheme": "file",
        "format": "txt",
        "encoding": "utf-8",
        # TODO: improve in detector.detect_resource
        "mediatype": "application/txt",
        "stats": {
            "md5": "e1cbb0c3879af8347246f12c559a86b5",
            "sha256": "b9e68e1bea3e5b19ca6b2f98b73a54b73daafaa250484902e09982e07a12e733",
            "bytes": 5,
        },
    }


def test_resource_infer_from_path():
    resource = Resource("data/table.csv")
    resource.infer(stats=True)
    assert resource.path == "data/table.csv"


# Bugs


def test_resource_infer_not_slugified_name_issue_531():
    resource = Resource("data/Table With Data.csv")
    resource.infer(stats=True)
    assert resource.name == "table-with-data"
