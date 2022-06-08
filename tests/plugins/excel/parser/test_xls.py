import pytest
from frictionless import Resource, Layout, FrictionlessException, helpers
from frictionless.plugins.excel import ExcelDialect


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


def test_xls_parser():
    with Resource("data/table.xls") as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_xls_parser_remote():
    with Resource(BASEURL % "data/table.xls") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_xls_parser_sheet_by_index():
    source = "data/sheet2.xls"
    dialect = ExcelDialect(sheet=2)
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_xls_parser_sheet_by_index_not_existent():
    source = "data/sheet2.xls"
    dialect = ExcelDialect(sheet=3)
    with pytest.raises(FrictionlessException) as excinfo:
        Resource(source, dialect=dialect).open()
    assert 'sheet "3"' in str(excinfo.value)


def test_xls_parser_sheet_by_name():
    source = "data/sheet2.xls"
    dialect = ExcelDialect(sheet="Sheet2")
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_xls_parser_sheet_by_name_not_existent():
    source = "data/sheet2.xls"
    dialect = ExcelDialect(sheet="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource(source, dialect=dialect).open()
    assert 'sheet "bad"' in str(excinfo.value)


def test_xls_parser_merged_cells():
    source = "data/merged-cells.xls"
    layout = Layout(header=False)
    with Resource(source, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": "data", "field2": None},
            {"field1": None, "field2": None},
            {"field1": None, "field2": None},
        ]


def test_xls_parser_merged_cells_fill():
    source = "data/merged-cells.xls"
    dialect = ExcelDialect(fill_merged_cells=True)
    layout = Layout(header=False)
    with Resource(source, dialect=dialect, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": "data", "field2": "data"},
            {"field1": "data", "field2": "data"},
            {"field1": "data", "field2": "data"},
        ]


def test_xls_parser_with_boolean():
    with Resource("data/table-with-booleans.xls") as resource:
        assert resource.header == ["id", "boolean"]
        assert resource.read_rows() == [
            {"id": 1, "boolean": True},
            {"id": 2, "boolean": False},
        ]


# Write


def test_xls_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.xls")))
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_xls_parser_write_sheet_name(tmpdir):
    dialect = ExcelDialect(sheet="sheet")
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.xls")), dialect=dialect)
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
