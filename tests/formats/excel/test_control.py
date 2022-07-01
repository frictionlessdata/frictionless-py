from frictionless import Resource, formats


# General


def test_excel_dialect():
    with Resource("data/table.xlsx") as resource:
        assert isinstance(resource.dialect.get_control("excel"), formats.ExcelControl)
