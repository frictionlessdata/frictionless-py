import io
import pytest
from decimal import Decimal
from frictionless import Resource, Dialect, Layout, Detector, helpers
from frictionless import FrictionlessException
from frictionless.plugins.excel import ExcelControl


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


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
    dialect = Dialect(controls=[ExcelControl(sheet=2)])
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


def test_xlsx_parser_format_error_sheet_by_index_not_existent():
    source = "data/sheet2.xlsx"
    dialect = Dialect(controls=[ExcelControl(sheet=3)])
    resource = Resource(source, dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'Excel document "data/sheet2.xlsx" does not have a sheet "3"'


def test_xlsx_parser_sheet_by_name():
    source = "data/sheet2.xlsx"
    dialect = Dialect(controls=[ExcelControl(sheet="Sheet2")])
    with Resource(source, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


def test_xlsx_parser_format_errors_sheet_by_name_not_existent():
    source = "data/sheet2.xlsx"
    dialect = Dialect(controls=[ExcelControl(sheet="bad")])
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
    dialect = Dialect(controls=[ExcelControl(fill_merged_cells=True)])
    layout = Layout(header=False)
    with Resource(source, dialect=dialect, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": "data", "field2": "data"},
            {"field1": "data", "field2": "data"},
            {"field1": "data", "field2": "data"},
        ]


def test_xlsx_parser_adjust_floating_point_error():
    source = "data/adjust-floating-point-error.xlsx"
    dialect = Dialect(
        controls=[
            ExcelControl(
                fill_merged_cells=False,
                preserve_formatting=True,
                adjust_floating_point_error=True,
            )
        ]
    )
    layout = Layout(skip_fields=["<blank>"])
    with Resource(source, dialect=dialect, layout=layout) as resource:
        assert resource.read_rows()[1].cells[2] == 274.66


def test_xlsx_parser_adjust_floating_point_error_default():
    source = "data/adjust-floating-point-error.xlsx"
    dialect = Dialect(controls=[ExcelControl(preserve_formatting=True)])
    layout = Layout(skip_fields=["<blank>"])
    with Resource(source, dialect=dialect, layout=layout) as resource:
        assert resource.read_rows()[1].cells[2] == 274.65999999999997


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_xlsx_parser_preserve_formatting():
    source = "data/preserve-formatting.xlsx"
    dialect = Dialect(controls=[ExcelControl(preserve_formatting=True)])
    layout = Layout(header_rows=[1])
    detector = Detector(field_type="any")
    with Resource(source, dialect=dialect, layout=layout, detector=detector) as resource:
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
    dialect = Dialect(controls=[ExcelControl(preserve_formatting=True)])
    with Resource(source, dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"col1": 123, "col2": "52.00%"},
            {"col1": 456, "col2": "30.00%"},
            {"col1": 789, "col2": "6.00%"},
        ]


def test_xlsx_parser_preserve_formatting_number_multicode():
    source = "data/number-format-multicode.xlsx"
    dialect = Dialect(controls=[ExcelControl(preserve_formatting=True)])
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
        dialect = Dialect(controls=[ExcelControl(sheet=sheet, workbook_cache={})])
        with Resource(source, dialect=dialect) as resource:
            assert len(dialect.get_control("excel").workbook_cache) == 1
            assert resource.read_rows()


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
    dialect = Dialect(controls=[ExcelControl(fill_merged_cells=True)])
    layout = Layout(header=False)
    with Resource(source, dialect=dialect, layout=layout) as resource:
        assert resource.read_rows() == [
            {"field1": True, "field2": True},
            {"field1": True, "field2": True},
            {"field1": True, "field2": True},
        ]


@pytest.mark.vcr
def test_xlsx_parser_fix_for_2007_xls():
    source = "https://ams3.digitaloceanspaces.com/budgetkey-files/spending-reports/2018-3-משרד התרבות והספורט-לשכת הפרסום הממשלתית-2018-10-22-c457.xls"
    with Resource(source, format="xlsx") as resource:
        assert len(resource.read_rows()) > 10


# Write


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


@pytest.mark.skip
def test_xlsx_parser_write_sheet_name(tmpdir):
    dialect = Dialect(controls=[ExcelControl(sheet="sheet")])
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.xlsx")), dialect=dialect)
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Problems


def test_xlsx_parser_multiline_header_with_merged_cells_issue_1024():
    layout = Layout(header_rows=[10, 11, 12])
    dialect = Dialect(controls=[ExcelControl(sheet="IPC", fill_merged_cells=True)])
    with Resource("data/issue-1024.xlsx", dialect=dialect, layout=layout) as resource:
        assert resource.header
        assert resource.header[21] == "Current Phase P3+ #"


def test_xlsx_parser_stats_no_bytes_and_hash_issue_938():
    resource = Resource("data/table.xlsx")
    resource.infer(stats=True)
    assert resource.stats["hash"] == "dddeae0cad9b46e8d7a2d157774dcf5b"
    assert resource.stats["bytes"] == 6230
