from frictionless import Package


# General


def test_excel_adapter_package():
    package = Package("data/table.ods")
    assert package.to_descriptor() == {
        "resources": [
            {
                "name": "list1",
                "path": "data/table.ods",
                "dialect": {"ods": {"sheet": "Лист1"}},
            },
        ]
    }
