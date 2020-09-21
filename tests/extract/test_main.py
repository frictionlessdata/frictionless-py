from frictionless import extract


# General


def test_extract():
    assert extract("data/table.csv") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_source_type():
    assert extract("data/package.json", source_type="package") == {
        "data/table.csv": [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }
