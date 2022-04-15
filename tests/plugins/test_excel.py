import io
import pytest
from decimal import Decimal
from datetime import datetime
from frictionless import Resource, Layout, Detector, FrictionlessException, helpers
from frictionless.plugins.excel import ExcelDialect

IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Parser


def test_xlsx_parser_table():
    source = io.open("data/table.xlsx", mode="rb")
    with Resource(source, format="xlsx") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_xlsx_parser_remote():
    source = BASEURL % "data/table.xlsx"
    with Resource(source) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


def test_xlsx_parser_sheet_by_index():
    source = "data/sheet2.xlsx"
    dialect = ExcelDialect(sheet=2)
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


def test_xlsx_parser_format_error_sheet_by_index_not_existent():
    source = "data/sheet2.xlsx"
    dialect = ExcelDialect(sheet=3)
    resource = Resource(source, dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'Excel document "data/sheet2.xlsx" does not have a sheet "3"'


def test_xlsx_parser_sheet_by_name():
    source = "data/sheet2.xlsx"
    dialect = ExcelDialect(sheet="Sheet2")
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


def test_xlsx_parser_format_errors_sheet_by_name_not_existent():
    source = "data/sheet2.xlsx"
    dialect = ExcelDialect(sheet="bad")
    resource = Resource(source, dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'Excel document "data/sheet2.xlsx" does not have a sheet "bad"'


def test_xlsx_parser_merged_cells():
    source = "data/merged-cells.xlsx"
    layout = Layout(header=False)
    with Resource(source, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": "data", "field2": None},
        ]


def test_xlsx_parser_merged_cells_fill():
    source = "data/merged-cells.xlsx"
    dialect = ExcelDialect(fill_merged_cells=True)
    layout = Layout(header=False)
    with Resource(source, dialect=dialect, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": "data", "field2": "data"},
            {"field1": "data", "field2": "data"},
            {"field1": "data", "field2": "data"},
        ]


def test_xlsx_parser_adjust_floating_point_error():
    source = "data/adjust-floating-point-error.xlsx"
    dialect = ExcelDialect(
        fill_merged_cells=False,
        preserve_formatting=True,
        adjust_floating_point_error=True,
    )
    layout = Layout(skip_fields=["<blank>"])
    with pytest.warns(UserWarning):
        with Resource(source, dialect=dialect, layout=layout) as resource:
            assert resource.read_rows()[1].cells[2] == 274.66


def test_xlsx_parser_adjust_floating_point_error_default():
    source = "data/adjust-floating-point-error.xlsx"
    dialect = ExcelDialect(preserve_formatting=True)
    layout = Layout(skip_fields=["<blank>"])
    with pytest.warns(UserWarning):
        with Resource(source, dialect=dialect, layout=layout) as resource:
            assert resource.read_rows()[1].cells[2] == 274.65999999999997


def test_xlsx_parser_preserve_formatting():
    source = "data/preserve-formatting.xlsx"
    dialect = ExcelDialect(preserve_formatting=True)
    layout = Layout(header_rows=[1])
    detector = Detector(field_type="any")
    if IS_UNIX:
        with Resource(
            source, dialect=dialect, layout=layout, detector=detector
        ) as resource:
            assert resource.read_rows() == [
                {
                    # general
                    "empty": None,
                    # numeric
                    "0": "1001",
                    "0.00": "1000.56",
                    "0.0000": "1000.5577",
                    "0.00000": "1000.55770",
                    "0.0000#": "1000.5577",
                    # temporal
                    "m/d/yy": "5/20/40",
                    "d-mmm": "20-May",
                    "mm/dd/yy": "05/20/40",
                    "mmddyy": "052040",
                    "mmddyyam/pmdd": "052040AM20",
                }
            ]


def test_xlsx_parser_preserve_formatting_percentage():
    source = "data/preserve-formatting-percentage.xlsx"
    dialect = ExcelDialect(preserve_formatting=True)
    with Resource(source, dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"col1": 123, "col2": "52.00%"},
            {"col1": 456, "col2": "30.00%"},
            {"col1": 789, "col2": "6.00%"},
        ]


def test_xlsx_parser_preserve_formatting_number_multicode():
    source = "data/number-format-multicode.xlsx"
    dialect = ExcelDialect(preserve_formatting=True)
    layout = Layout(skip_fields=["<blank>"])
    with Resource(source, dialect=dialect, layout=layout) as resource:
        assert resource.read_rows() == [
            {"col1": Decimal("4.5")},
            {"col1": Decimal("-9.032")},
            {"col1": Decimal("15.8")},
        ]


@pytest.mark.vcr
def test_xlsx_parser_workbook_cache():
    source = BASEURL % "data/sheets.xlsx"
    for sheet in ["Sheet1", "Sheet2", "Sheet3"]:
        dialect = ExcelDialect(sheet=sheet, workbook_cache={})
        with Resource(source, dialect=dialect) as resource:
            assert len(dialect.workbook_cache) == 1
            assert resource.read_rows()


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


def test_xlsx_parser_merged_cells_boolean():
    source = "data/merged-cells-boolean.xls"
    layout = Layout(header=False)
    with Resource(source, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": True, "field2": None},
            {"field1": None, "field2": None},
            {"field1": None, "field2": None},
        ]


def test_xlsx_parser_merged_cells_fill_boolean():
    source = "data/merged-cells-boolean.xls"
    dialect = ExcelDialect(fill_merged_cells=True)
    layout = Layout(header=False)
    with Resource(source, dialect=dialect, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": True, "field2": True},
            {"field1": True, "field2": True},
            {"field1": True, "field2": True},
        ]


def test_xls_parser_with_ints_floats_dates():
    source = "data/table-with-ints-floats-dates.xls"
    with Resource(source) as resource:
        assert resource.header == ["Int", "Float", "Date"]
        assert resource.read_rows() == [
            {"Int": 2013, "Float": Decimal("3.3"), "Date": datetime(2009, 8, 16)},
            {"Int": 1997, "Float": Decimal("5.6"), "Date": datetime(2009, 9, 20)},
            {"Int": 1969, "Float": Decimal("11.7"), "Date": datetime(2012, 8, 23)},
        ]


@pytest.mark.vcr
def test_xlsx_parser_fix_for_2007_xls():
    source = "https://ams3.digitaloceanspaces.com/budgetkey-files/spending-reports/2018-3-משרד התרבות והספורט-לשכת הפרסום הממשלתית-2018-10-22-c457.xls"
    with Resource(source, format="xlsx") as resource:
        assert len(resource.read_rows()) > 10


def test_xlsx_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.xlsx")))
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_xlsx_parser_write_sheet_name(tmpdir):
    dialect = ExcelDialect(sheet="sheet")
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.xlsx")), dialect=dialect)
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


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


# Issues


def test_xlsx_parser_multiline_header_with_merged_cells_issue_1024():
    layout = Layout(header_rows=[10, 11, 12])
    dialect = ExcelDialect(sheet="IPC", fill_merged_cells=True)
    with Resource('data/issue-1024.xlsx', dialect=dialect, layout=layout) as resource:
        assert resource.header
        assert resource.header[21] == 'Current Phase P3+ #'
