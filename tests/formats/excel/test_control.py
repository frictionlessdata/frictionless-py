from frictionless import Resource
from frictionless.plugins.excel import ExcelControl


# General


def test_excel_dialect():
    with Resource("data/table.xlsx") as resource:
        assert isinstance(resource.dialect.get_control("excel"), ExcelControl)
