from frictionless import Package

# General


def test_extract_package():
    package = Package(["data/table.csv"])
    assert package.extract() == {
        "table": [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
    }


def test_extract_package_process():
    package = Package(["data/table.csv"])
    process = lambda row: {**row.to_dict(), "id": 3}
    assert package.extract(process=process) == {
        "table": [
            {"id": 3, "name": "english"},
            {"id": 3, "name": "中国人"},
        ]
    }


def test_extract_package_descriptor_type_package():
    package = Package("data/package/datapackage.json")
    assert package.extract()
