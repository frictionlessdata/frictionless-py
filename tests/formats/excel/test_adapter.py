from frictionless import Package


# General


def test_excel_adapter_package():
    package = Package("data/sheets.xlsx")
    assert package.to_descriptor() == {
        "resources": [
            {
                "name": "sheet1",
                "path": "data/sheets.xlsx",
                "dialect": {"excel": {"sheet": "Sheet1"}},
            },
            {
                "name": "sheet2",
                "path": "data/sheets.xlsx",
                "dialect": {"excel": {"sheet": "Sheet2"}},
            },
            {
                "name": "sheet3",
                "path": "data/sheets.xlsx",
                "dialect": {"excel": {"sheet": "Sheet3"}},
            },
        ]
    }
