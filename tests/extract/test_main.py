from frictionless import Resource, extract, helpers


IS_UNIX = not helpers.is_platform("windows")


# General


def test_extract():
    assert extract("data/table.csv") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_type_package():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
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
