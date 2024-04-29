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


def test_excel_adapter_package_two_sheets():
    package = Package("data/table-with-two-sheets.ods")
    assert package.to_descriptor() == {
        "resources": [
            {
                "name": "list1",
                "type": "table",
                "path": "data/table-with-two-sheets.ods",
                "scheme": "file",
                "format": "ods",
                "mediatype": "application/vnd.oasis.opendocument.spreadsheet",
                "dialect": {"ods": {"sheet": "Лист1"}},
            },
            {
                "name": "tabelle2",
                "type": "table",
                "path": "data/table-with-two-sheets.ods",
                "scheme": "file",
                "format": "ods",
                "mediatype": "application/vnd.oasis.opendocument.spreadsheet",
                "dialect": {"ods": {"sheet": "Tabelle2"}},
            },
        ],
    }
