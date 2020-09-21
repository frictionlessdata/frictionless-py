from frictionless import extract


# General


def test_extract_resource():
    assert extract("data/resource.json") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_process():
    process = lambda row: row.to_list()
    assert extract("data/resource.json", process=process) == [
        [1, "english"],
        [2, "中国人"],
    ]
