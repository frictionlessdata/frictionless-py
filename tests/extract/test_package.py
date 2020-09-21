from frictionless import extract


# General


def test_extract_package():
    assert extract("data/package.json") == {
        "data/table.csv": [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }
