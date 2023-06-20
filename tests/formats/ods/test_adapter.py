from frictionless import Package

# General


def test_excel_adapter_package():
    package = Package("data/table.ods")
    assert package.to_descriptor() == {
        "resources": [
            {
                "name": "list1",
                "type": "table",
                "path": "data/table.ods",
                "scheme": "file",
                "format": "ods",
                "mediatype": "application/vnd.oasis.opendocument.spreadsheet",
                "dialect": {"ods": {"sheet": "Лист1"}},
            },
        ],
    }
