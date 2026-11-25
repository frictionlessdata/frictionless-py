import json
import zipfile
from pathlib import Path

import pytest

from frictionless.console import console

from .conftest import create_runner

runner = create_runner()
ODS_PATH = "data/table-with-two-sheets.ods"


@pytest.mark.parametrize(
    "source_mode", ["source", "format", "descriptor", "basepath", "archive"]
)
def test_console_describe_ods_sheet(source_mode, tmp_path):
    args = [ODS_PATH]
    if source_mode == "format":
        path = tmp_path / "workbook.xls"
        path.write_bytes(Path(ODS_PATH).read_bytes())
        args = [str(path), "--format", "ods"]
    elif source_mode == "descriptor":
        path = tmp_path / "resource.json"
        (tmp_path / "workbook.ods").write_bytes(Path(ODS_PATH).read_bytes())
        path.write_text(json.dumps({"name": "workbook", "path": "workbook.ods"}))
        args = [str(path)]
    elif source_mode == "basepath":
        args = ["table-with-two-sheets.ods", "--basepath", "data"]
    elif source_mode == "archive":
        path = tmp_path / "workbook.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.write(ODS_PATH, "nested/workbook.ods")
        args = [str(path), "--innerpath", "nested/workbook.ods"]

    result = runner.invoke(console, ["describe", *args, "--sheet", "Tabelle2", "--json"])

    assert result.exit_code == 0, result.output
    descriptor = json.loads(result.stdout)
    assert descriptor["schema"]["fields"] == [
        {"name": "a", "type": "integer"},
        {"name": "b", "type": "integer"},
        {"name": "c", "type": "integer"},
    ]
    assert descriptor["dialect"] == {"ods": {"sheet": "Tabelle2"}}


def test_console_describe_ods_sheet_overrides_dialect():
    dialect = {"ods": {"sheet": "Лист1"}, "commentChar": "#"}
    result = runner.invoke(
        console,
        [
            "describe",
            ODS_PATH,
            "--sheet",
            "Tabelle2",
            "--json",
            "--dialect",
            json.dumps(dialect),
        ],
    )

    assert result.exit_code == 0, result.output
    descriptor = json.loads(result.stdout)
    assert [field["name"] for field in descriptor["schema"]["fields"]] == ["a", "b", "c"]
    assert descriptor["dialect"] == {"ods": {"sheet": "Tabelle2"}, "commentChar": "#"}


def test_console_describe_ods_default_sheet():
    result = runner.invoke(console, ["describe", ODS_PATH, "--json"])

    assert result.exit_code == 0, result.output
    descriptor = json.loads(result.stdout)
    assert [field["name"] for field in descriptor["schema"]["fields"]] == ["id", "name"]


def test_console_extract_ods_sheet():
    result = runner.invoke(
        console, ["extract", ODS_PATH, "--sheet", "Tabelle2", "--json"]
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {
        "table-with-two-sheets": [{"a": 1, "b": 2, "c": 3}]
    }


@pytest.mark.parametrize("command", ["describe", "extract"])
def test_console_ods_missing_sheet(command):
    result = runner.invoke(
        console, [command, ODS_PATH, "--sheet", "MissingSheet", "--json"]
    )

    assert result.exit_code == 1
    assert "[format-error]" in result.stderr
    assert '"MissingSheet"' in result.stderr


@pytest.mark.parametrize("extension", ["xls", "xlsx"])
def test_console_describe_excel_sheet(extension):
    result = runner.invoke(
        console, ["describe", f"data/sheet2.{extension}", "--sheet", "Sheet2", "--json"]
    )

    assert result.exit_code == 0, result.output
    descriptor = json.loads(result.stdout)
    assert [field["name"] for field in descriptor["schema"]["fields"]] == ["id", "name"]
    assert descriptor["dialect"] == {"excel": {"sheet": "Sheet2"}}


def test_console_list_ods_sheet():
    result = runner.invoke(console, ["list", ODS_PATH, "--sheet", "Tabelle2", "--json"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)[0]["dialect"] == {"ods": {"sheet": "Tabelle2"}}


def test_console_validate_ods_sheet():
    result = runner.invoke(
        console, ["validate", ODS_PATH, "--sheet", "Tabelle2", "--json"]
    )

    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert report["valid"]
    assert report["tasks"][0]["labels"] == ["a", "b", "c"]


def test_console_convert_ods_sheet(tmp_path):
    path = tmp_path / "output.csv"
    result = runner.invoke(
        console, ["convert", ODS_PATH, "--sheet", "Tabelle2", "--to-path", str(path)]
    )

    assert result.exit_code == 0, result.output
    assert path.read_text(encoding="utf-8").splitlines() == ["a,b,c", "1,2,3"]
