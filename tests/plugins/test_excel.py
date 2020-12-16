import io
import pytest
from datetime import datetime
from frictionless import Table, Query, FrictionlessException, helpers
from frictionless.plugins.excel import ExcelDialect

BASE_URL = "https://raw.githubusercontent.com/frictionlessdata/tabulator-py/master/%s"


# Read


def test_xlsx_parser_table():
    source = io.open("data/table.xlsx", mode="rb")
    with Table(source, format="xlsx") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1.0, "english"], [2.0, "中国人"]]


@pytest.mark.vcr
def test_xlsx_parser_remote():
    source = BASE_URL % "data/table.xlsx"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1.0, "english"], [2.0, "中国人"]]


def test_xlsx_parser_sheet_by_index():
    source = "data/sheet2.xlsx"
    dialect = ExcelDialect(sheet=2)
    with Table(source, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1.0, "english"], [2.0, "中国人"]]


def test_xlsx_parser_format_error_sheet_by_index_not_existent():
    source = "data/sheet2.xlsx"
    dialect = ExcelDialect(sheet=3)
    table = Table(source, dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'Excel document "data/sheet2.xlsx" does not have a sheet "3"'


def test_xlsx_parser_sheet_by_name():
    source = "data/sheet2.xlsx"
    dialect = ExcelDialect(sheet="Sheet2")
    with Table(source, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1.0, "english"], [2.0, "中国人"]]


def test_xlsx_parser_format_errors_sheet_by_name_not_existent():
    source = "data/sheet2.xlsx"
    dialect = ExcelDialect(sheet="bad")
    table = Table(source, dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'Excel document "data/sheet2.xlsx" does not have a sheet "bad"'


def test_xlsx_parser_merged_cells():
    source = "data/merged-cells.xlsx"
    with Table(source, headers=False) as table:
        assert table.read_data() == [["data", None]]


def test_xlsx_parser_merged_cells_fill():
    source = "data/merged-cells.xlsx"
    dialect = ExcelDialect(fill_merged_cells=True)
    with Table(source, dialect=dialect, headers=False) as table:
        assert table.read_data() == [["data", "data"], ["data", "data"], ["data", "data"]]


def test_xlsx_parser_adjust_floating_point_error():
    source = "data/adjust-floating-point-error.xlsx"
    dialect = ExcelDialect(
        fill_merged_cells=False,
        preserve_formatting=True,
        adjust_floating_point_error=True,
    )
    query = Query(skip_fields=["<blank>"])
    with pytest.warns(UserWarning):
        with Table(source, dialect=dialect, query=query) as table:
            assert table.read_data()[1][2] == 274.66


def test_xlsx_parser_adjust_floating_point_error_default():
    source = "data/adjust-floating-point-error.xlsx"
    dialect = ExcelDialect(preserve_formatting=True)
    query = Query(skip_fields=["<blank>"])
    with pytest.warns(UserWarning):
        with Table(source, dialect=dialect, query=query) as table:
            assert table.read_data()[1][2] == 274.65999999999997


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_xlsx_parser_preserve_formatting():
    source = "data/preserve-formatting.xlsx"
    dialect = ExcelDialect(preserve_formatting=True)
    with Table(source, dialect=dialect, headers=1, infer_type="any") as table:
        assert table.read_rows() == [
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
    with Table(source, dialect=dialect) as table:
        assert table.read_data() == [
            [123, "52.00%"],
            [456, "30.00%"],
            [789, "6.00%"],
        ]


def test_xlsx_parser_preserve_formatting_number_multicode():
    source = "data/number-format-multicode.xlsx"
    dialect = ExcelDialect(preserve_formatting=True)
    query = Query(skip_fields=["<blank>"])
    with Table(source, dialect=dialect, query=query) as table:
        assert table.read_data() == [["4.5"], ["-9.032"], ["15.8"]]


@pytest.mark.vcr
def test_xlsx_parser_workbook_cache():
    source = BASE_URL % "data/special/sheets.xlsx"
    for sheet in ["Sheet1", "Sheet2", "Sheet3"]:
        dialect = ExcelDialect(sheet=sheet, workbook_cache={})
        with Table(source, dialect=dialect) as table:
            assert len(dialect.workbook_cache) == 1
            assert table.read_data()


def test_table_local_xls():
    with Table("data/table.xls") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


@pytest.mark.vcr
def test_table_remote_xls():
    with Table(BASE_URL % "data/table.xls") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_xls_parser_sheet_by_index():
    source = "data/sheet2.xls"
    dialect = ExcelDialect(sheet=2)
    with Table(source, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_xls_parser_sheet_by_index_not_existent():
    source = "data/sheet2.xls"
    dialect = ExcelDialect(sheet=3)
    with pytest.raises(FrictionlessException) as excinfo:
        Table(source, dialect=dialect).open()
    assert 'sheet "3"' in str(excinfo.value)


def test_xls_parser_sheet_by_name():
    source = "data/sheet2.xls"
    dialect = ExcelDialect(sheet="Sheet2")
    with Table(source, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_xls_parser_sheet_by_name_not_existent():
    source = "data/sheet2.xls"
    dialect = ExcelDialect(sheet="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        Table(source, dialect=dialect).open()
    assert 'sheet "bad"' in str(excinfo.value)


def test_xls_parser_merged_cells():
    source = "data/merged-cells.xls"
    with Table(source, headers=False) as table:
        assert table.read_data() == [["data", ""], ["", ""], ["", ""]]


def test_xls_parser_merged_cells_fill():
    source = "data/merged-cells.xls"
    dialect = ExcelDialect(fill_merged_cells=True)
    with Table(source, dialect=dialect, headers=False) as table:
        assert table.read_data() == [["data", "data"], ["data", "data"], ["data", "data"]]


def test_xls_parser_with_boolean():
    with Table("data/table-with-booleans.xls") as table:
        assert table.header == ["id", "boolean"]
        assert table.read_data() == [[1, True], [2, False]]


def test_xlsx_parser_merged_cells_boolean():
    source = "data/merged-cells-boolean.xls"
    with Table(source, headers=False) as table:
        assert table.read_data() == [[True, ""], ["", ""], ["", ""]]


def test_xlsx_parser_merged_cells_fill_boolean():
    source = "data/merged-cells-boolean.xls"
    dialect = ExcelDialect(fill_merged_cells=True)
    with Table(source, dialect=dialect, headers=False) as table:
        assert table.read_data() == [[True, True], [True, True], [True, True]]


def test_xls_parser_with_ints_floats_dates():
    source = "data/table-with-ints-floats-dates.xls"
    with Table(source) as table:
        assert table.header == ["Int", "Float", "Date"]
        assert table.read_data() == [
            [2013, 3.3, datetime(2009, 8, 16)],
            [1997, 5.6, datetime(2009, 9, 20)],
            [1969, 11.7, datetime(2012, 8, 23)],
        ]


@pytest.mark.skip
@pytest.mark.vcr
def test_xls_parser_fix_for_2007_xls():
    source = "https://ams3.digitaloceanspaces.com/budgetkey-files/spending-reports/2018-3-משרד התרבות והספורט-לשכת הפרסום הממשלתית-2018-10-22-c457.xls"
    with Table(source) as table:
        assert len(table.read_data()) > 10


# Write


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_xlsx_parser_write(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.xlsx"))
    with Table(source) as table:
        table.write(target)
    with Table(target) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_xlsx_parser_write_sheet_name(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.xlsx"))
    dialect = ExcelDialect(sheet="sheet")
    with Table(source) as table:
        table.write(target, dialect=dialect)
    with Table(target, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_xls_parser_write(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.xls"))
    with Table(source) as table:
        table.write(target)
    with Table(target) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_xls_parser_write_sheet_name(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.xls"))
    dialect = ExcelDialect(sheet="sheet")
    with Table(source) as table:
        table.write(target, dialect=dialect)
    with Table(target, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]
