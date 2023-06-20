import io
from decimal import Decimal

import pytest

from frictionless import Detector, Dialect, FrictionlessException, Package, formats
from frictionless import platform
from frictionless.resources import TableResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


def test_xlsx_parser_table():
    data = io.open("data/table.xlsx", mode="rb")
    with TableResource(data=data, format="xlsx") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_xlsx_parser_remote():
    path = BASEURL % "data/table.xlsx"
    with TableResource(path=path) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


def test_xlsx_parser_sheet_by_index():
    path = "data/sheet2.xlsx"
    control = formats.ExcelControl(sheet=2)
    with TableResource(path=path, control=control) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


def test_xlsx_parser_format_error_sheet_by_index_not_existent():
    path = "data/sheet2.xlsx"
    control = formats.ExcelControl(sheet=3)
    resource = TableResource(path=path, control=control)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "format-error"
    assert error.note == 'Excel document "data/sheet2.xlsx" does not have a sheet "3"'


def test_xlsx_parser_sheet_by_name():
    path = "data/sheet2.xlsx"
    control = formats.ExcelControl(sheet="Sheet2")
    with TableResource(path=path, control=control) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1.0, "name": "english"},
            {"id": 2.0, "name": "中国人"},
        ]


def test_xlsx_parser_format_errors_sheet_by_name_not_existent():
    path = "data/sheet2.xlsx"
    control = formats.ExcelControl(sheet="bad")
    resource = TableResource(path=path, control=control)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "format-error"
    assert error.note == 'Excel document "data/sheet2.xlsx" does not have a sheet "bad"'


def test_xlsx_parser_merged_cells():
    path = "data/merged-cells.xlsx"
    dialect = Dialect(header=False)
    with TableResource(path=path, dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"field1": "data", "field2": None},
        ]


def test_xlsx_parser_merged_cells_fill():
    path = "data/merged-cells.xlsx"
    control = formats.ExcelControl(fill_merged_cells=True)
    dialect = Dialect(header=False, controls=[control])
    with TableResource(path=path, dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"field1": "data", "field2": "data"},
            {"field1": "data", "field2": "data"},
            {"field1": "data", "field2": "data"},
        ]


def test_xlsx_parser_adjust_floating_point_error():
    path = "data/adjust-floating-point-error.xlsx"
    control = formats.ExcelControl(
        fill_merged_cells=False,
        preserve_formatting=True,
        adjust_floating_point_error=True,
    )
    with TableResource(path=path, control=control) as resource:
        assert resource.read_rows()[1].cells[2] == 274.66


def test_xlsx_parser_adjust_floating_point_error_default():
    path = "data/adjust-floating-point-error.xlsx"
    control = formats.ExcelControl(preserve_formatting=True)
    with TableResource(path=path, control=control) as resource:
        assert resource.read_rows()[1].cells[2] == 274.65999999999997


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_xlsx_parser_preserve_formatting():
    path = "data/preserve-formatting.xlsx"
    control = formats.ExcelControl(preserve_formatting=True)
    detector = Detector(field_type="any")
    with TableResource(path=path, control=control, detector=detector) as resource:
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
    path = "data/preserve-formatting-percentage.xlsx"
    control = formats.ExcelControl(preserve_formatting=True)
    with TableResource(path=path, control=control) as resource:
        assert resource.read_rows() == [
            {"col1": 123, "col2": "52.00%"},
            {"col1": 456, "col2": "30.00%"},
            {"col1": 789, "col2": "6.00%"},
        ]


def test_xlsx_parser_preserve_formatting_number_multicode():
    path = "data/number-format-multicode.xlsx"
    control = formats.ExcelControl(preserve_formatting=True)
    with TableResource(path=path, control=control) as resource:
        assert resource.read_rows() == [
            {"col1": Decimal("4.5")},
            {"col1": Decimal("-9.032")},
            {"col1": Decimal("15.8")},
        ]


@pytest.mark.vcr
def test_xlsx_parser_workbook_cache():
    path = BASEURL % "data/sheets.xlsx"
    for sheet in ["Sheet1", "Sheet2", "Sheet3"]:
        control = formats.ExcelControl(sheet=sheet, workbook_cache={})
        with TableResource(path=path, control=control) as resource:
            control = resource.dialect.get_control("excel")
            assert isinstance(control, formats.ExcelControl)
            assert len(control.workbook_cache) == 1  # type: ignore
            assert resource.read_rows()


def test_xlsx_parser_merged_cells_boolean():
    path = "data/merged-cells-boolean.xls"
    dialect = Dialect(header=False)
    with TableResource(path=path, dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"field1": True, "field2": None},
            {"field1": None, "field2": None},
            {"field1": None, "field2": None},
        ]


def test_xlsx_parser_merged_cells_fill_boolean():
    path = "data/merged-cells-boolean.xls"
    control = formats.ExcelControl(fill_merged_cells=True)
    dialect = Dialect(header=False, controls=[control])
    with TableResource(path=path, dialect=dialect) as resource:
        assert resource.read_rows() == [
            {"field1": True, "field2": True},
            {"field1": True, "field2": True},
            {"field1": True, "field2": True},
        ]


@pytest.mark.vcr
def test_xlsx_parser_fix_for_2007_xls():
    path = "https://ams3.digitaloceanspaces.com/budgetkey-files/spending-reports/2018-3-משרד התרבות והספורט-לשכת הפרסום הממשלתית-2018-10-22-c457.xls"
    with TableResource(path=path, format="xlsx") as resource:
        assert len(resource.read_rows()) > 10


# Write


def test_xlsx_parser_write(tmpdir):
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.xlsx")))
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_xlsx_parser_write_sheet_name(tmpdir):
    control = formats.ExcelControl(sheet="sheet")
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.xlsx")), control=control)
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_xlsx_parser_write_skip_header(tmpdir):
    control = formats.ExcelControl(sheet="sheet")
    dialect = Dialect.from_descriptor({"header": False})
    data = b"header1,header2\nvalue11,value12\nvalue21,value22"
    path = str(tmpdir.join("table.xlsx"))
    target = TableResource(path=path, dialect=dialect, control=control)
    with TableResource(data=data, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        resource.write_table(target)
    table = target.read_table()
    assert table.header == ["field1", "field2"]


# Bugs


def test_xlsx_parser_multiline_header_with_merged_cells_issue_1024():
    control = formats.ExcelControl(sheet="IPC", fill_merged_cells=True)
    dialect = Dialect(header_rows=[10, 11, 12], controls=[control])
    with TableResource(path="data/issue-1024.xlsx", dialect=dialect) as resource:
        assert resource.header
        assert resource.header[21] == "Current Phase P3+ #"


def test_xlsx_parser_stats_no_bytes_and_hash_issue_938():
    resource = TableResource(path="data/table.xlsx")
    resource.infer(stats=True)
    assert (
        resource.stats.sha256
        == "43a92d9620e900ef0b2f43fa3b8b5d123eb61716610940c8c498ce1e60a9c42a"
    )
    assert resource.stats.bytes == 6230


def test_xlsx_parser_cast_int_to_string_1251():
    descriptor = {
        "name": "example",
        "type": "table",
        "path": "data/cast-int-to-string-issue-1251.xlsx",
        "scheme": "file",
        "format": "xlsx",
        "encoding": "utf-8",
        "mediatype": "application/vnd.ms-excel",
        "schema": {
            "fields": [
                {"name": "A", "type": "string"},
                {"name": "B", "type": "string"},
                {"name": "C", "type": "string"},
                {"name": "D", "type": "any"},
                {"name": "E", "type": "integer"},
            ]
        },
    }
    resource = TableResource.from_descriptor(
        descriptor, control=formats.ExcelControl(stringified=True)
    )
    assert resource.read_rows() == [
        {"A": "001", "B": "b", "C": "1", "D": "a", "E": 1},
        {"A": "002", "B": "c", "C": "1", "D": "1", "E": 1},
    ]


@pytest.mark.vcr
def test_xlsx_parser_cannot_read_resource_from_remote_package_issue_1504():
    package = Package(
        "https://raw.githubusercontent.com/splor-mg/datapackage-reprex/main/20230512T084359/datapackage.json"
    )
    resource = package.get_table_resource("excel")
    table = resource.read_table()
    assert len(table.rows) == 4
