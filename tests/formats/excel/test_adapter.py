from frictionless import Package

# General


def test_excel_adapter_package():
    package = Package("data/sheets.xlsx")
    assert package.to_descriptor() == {
        "resources": [
            {
                "name": "sheet1",
                "type": "table",
                "path": "data/sheets.xlsx",
                "scheme": "file",
                "format": "xlsx",
                "mediatype": "application/vnd.ms-excel",
                "dialect": {"excel": {"sheet": "Sheet1"}},
            },
            {
                "name": "sheet2",
                "type": "table",
                "path": "data/sheets.xlsx",
                "scheme": "file",
                "format": "xlsx",
                "mediatype": "application/vnd.ms-excel",
                "dialect": {"excel": {"sheet": "Sheet2"}},
            },
            {
                "name": "sheet3",
                "type": "table",
                "path": "data/sheets.xlsx",
                "scheme": "file",
                "format": "xlsx",
                "mediatype": "application/vnd.ms-excel",
                "dialect": {"excel": {"sheet": "Sheet3"}},
            },
        ],
    }
