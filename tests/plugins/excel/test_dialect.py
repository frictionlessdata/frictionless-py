from frictionless import Resource
from frictionless.plugins.excel import ExcelDialect


# General


def test_excel_dialect():
    with Resource("data/table.xlsx") as resource:
        assert isinstance(resource.dialect, ExcelDialect)
