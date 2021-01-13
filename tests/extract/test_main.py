import pytest
from frictionless import Resource, extract, helpers


# General


def test_extract():
    assert extract("data/table.csv") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_type_package():
    assert extract("data/package.json", type="package") == {
        "data/table.csv": [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
    }


def test_extract_source_resource_instance():
    resource = Resource("data/table.csv")
    assert extract(resource) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
