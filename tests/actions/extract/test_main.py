from frictionless import Resource, extract, helpers


# General


def test_extract():
    assert extract("data/table.csv") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_type_package():
    path = "data/table.csv" if not helpers.is_platform("windows") else "data\\table.csv"
    assert extract("data/package.json", type="package") == {
        path: [
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
