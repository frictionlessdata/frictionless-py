import pytest
from frictionless import extract, helpers


# General


def test_extract():
    assert extract("data/table.csv") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_type_package():
    assert extract("data/package.json", type="package") == {
        "data/table.csv": [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }
