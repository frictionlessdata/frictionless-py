from frictionless import extract


# General


def test_extract_table():
    assert extract("data/table.csv") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
