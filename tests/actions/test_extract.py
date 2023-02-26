from frictionless import extract


# General


def test_extract():
    assert extract("data/table.csv") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_type_package():
    assert extract("data/package.json", type="package") == {
        "name": [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
    }


# Bugs


def test_extract_argument_descriptor_resource_issue_1362():
    assert extract(descriptor="data/resource.json") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_argument_descriptor_package_issue_1362():
    assert extract(descriptor="data/package.json", type="package") == {
        "name": [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
    }
