import json

import pytest
import yaml
from typer.testing import CliRunner

from frictionless import Detector, Dialect, extract, formats, platform
from frictionless.console import console

runner = CliRunner()


# General


def test_console_extract():
    actual = runner.invoke(console, "extract data/table.csv")
    assert actual.exit_code == 0
    assert actual.stdout.count("table")
    assert actual.stdout.count("id")
    assert actual.stdout.count("1")
    assert actual.stdout.count("2")


def test_console_extract_header_rows():
    actual = runner.invoke(console, "extract data/table.csv --json --header-rows '1,2'")
    expect = extract("data/table.csv", dialect=Dialect(header_rows=[1, 2]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_console_extract_header_join():
    actual = runner.invoke(
        console,
        "extract data/table.csv --json --header-rows '1,2' --header-join ':'",
    )
    expect = extract(
        "data/table.csv",
        dialect=Dialect(header_rows=[1, 2], header_join=":"),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_console_extract_comment_rows():
    actual = runner.invoke(console, "extract data/table.csv --json --comment-rows 1")
    expect = extract("data/table.csv", dialect=Dialect(comment_rows=[1]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_console_extract_schema():
    actual = runner.invoke(
        console,
        "extract data/table.csv --json --schema data/schema.json",
    )
    expect = extract(
        "data/table.csv",
        schema="data/schema.json",
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_console_extract_sync_schema():
    actual = runner.invoke(
        console,
        "extract data/table.csv --json --schema data/schema-reverse.json --schema-sync",
    )
    expect = extract(
        "data/table.csv",
        schema="data/schema.json",
        detector=Detector(schema_sync=True),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_console_extract_field_type():
    actual = runner.invoke(console, "extract data/table.csv --json --field-type string")
    expect = extract("data/table.csv", detector=Detector(field_type="string"))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_console_extract_field_names():
    actual = runner.invoke(console, "extract data/table.csv --json --field-names 'a,b'")
    expect = extract("data/table.csv", detector=Detector(field_names=["a", "b"]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_console_extract_field_missing_values():
    actual = runner.invoke(
        console, "extract data/table.csv --json --field-missing-values 1"
    )
    expect = extract(
        "data/table.csv",
        detector=Detector(field_missing_values=["1"]),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_console_extract_yaml():
    actual = runner.invoke(console, "extract data/table.csv --json")
    expect = extract("data/table.csv")
    assert actual.exit_code == 0
    assert yaml.safe_load(actual.stdout) == expect


def test_console_extract_json():
    actual = runner.invoke(console, "extract data/table.csv --json")
    expect = extract("data/table.csv")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_console_extract_csv():
    actual = runner.invoke(console, "extract data/table.csv --csv")
    with open("data/table.csv") as file:
        expect = file.read()
    assert actual.exit_code == 0
    assert actual.stdout == expect


def test_console_extract_dialect_sheet_option():
    actual = runner.invoke(console, "extract data/sheet2.xls --sheet Sheet2 --json")
    expect = extract("data/sheet2.xls", control=formats.ExcelControl(sheet="Sheet2"))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_console_extract_dialect_table_option_sql(sqlite_url_data):
    actual = runner.invoke(console, f"extract {sqlite_url_data} --table fruits --json")
    expect = extract(sqlite_url_data, control=formats.SqlControl(table="fruits"))
    assert json.loads(actual.stdout) == expect


@pytest.mark.skip
def test_console_extract_dialect_keyed_option():
    path = "data/table.keyed.json"
    actual = runner.invoke(console, f"extract --path {path} --keyed --json")
    expect = extract(path=path, control=formats.JsonControl(keyed=True))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


@pytest.mark.skip
def test_console_extract_dialect_keys_option():
    path = "data/table.keyed.json"
    actual = runner.invoke(console, f"extract --path {path} --keys 'name,id' --json")
    expect = extract(path=path, control=formats.JsonControl(keys=["name", "id"]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_console_extract_valid_rows():
    actual = runner.invoke(console, "extract data/countries.csv --valid --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {
        "countries": [
            {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
            {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
            {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
        ]
    }


def test_console_extract_yaml_valid_rows():
    actual = runner.invoke(console, "extract data/countries.csv --valid --yaml")
    assert actual.exit_code == 0
    assert yaml.safe_load(actual.stdout) == {
        "countries": [
            {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
            {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
            {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
        ]
    }


def test_console_extract_invalid_rows():
    actual = runner.invoke(console, "extract data/countries.csv --invalid --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {
        "countries": [
            {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
            {"id": 5, "neighbor_id": None, "name": None, "population": None},
        ]
    }


def test_console_extract_valid_rows_with_no_valid_rows():
    actual = runner.invoke(console, "extract data/invalid.csv --valid")
    assert actual.exit_code == 0
    assert actual.stdout.count("No rows found")


def test_console_extract_invalid_rows_with_no_invalid_rows():
    actual = runner.invoke(console, "extract data/capital-valid.csv --invalid")
    assert actual.exit_code == 0
    assert actual.stdout.count("No rows found")


def test_console_extract_valid_rows_from_datapackage_with_multiple_resources():
    actual = runner.invoke(console, "extract data/issue-1004.package.json --valid --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {
        "issue-1004-data1": [
            {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
            {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
            {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
        ],
        "issue-1004-data2": [],
    }


def test_console_extract_invalid_rows_from_datapackage_with_multiple_resources():
    actual = runner.invoke(
        console, "extract data/issue-1004.package.json --invalid --json"
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {
        "issue-1004-data1": [
            {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
            {"id": 5, "neighbor_id": None, "name": None, "population": None},
        ],
        "issue-1004-data2": [
            {"id": 1, "name": "english", "country": None, "city": None},
            {"id": 1, "name": "english", "country": None, "city": None},
            {"id": None, "name": None, "country": None, "city": None},
            {"id": 2, "name": "german", "country": 1, "city": 2},
        ],
    }


def test_console_extract_valid_rows_extract_dialect_sheet_option():
    actual = runner.invoke(
        console, "extract data/sheet2.xls --sheet Sheet2 --json --valid"
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {
        "sheet2": [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
    }


def test_console_extract_invalid_rows_extract_dialect_sheet_option():
    actual = runner.invoke(
        console, "extract data/sheet2.xls --sheet Sheet2 --json --invalid"
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {"sheet2": []}


def test_console_extract_single_resource():
    actual = runner.invoke(
        console, "extract data/datapackage.json --resource-name number-two --json"
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {
        "number-two": [
            {"id": 1, "name": "中国人"},
            {"id": 2, "name": "english"},
        ]
    }


def test_console_extract_single_invalid_resource():
    actual = runner.invoke(
        console, "extract data/datapackage.json --resource-name number-twoo"
    )
    assert actual.exit_code == 1
    assert actual.stdout.count("number-twoo")


def test_console_extract_single_valid_resource_invalid_package():
    actual = runner.invoke(
        console, "extract data/bad/datapackage.json --resource-name number-two"
    )
    assert actual.exit_code == 1
    assert actual.stdout.count("No such file or directory")


def test_console_extract_single_resource_yaml():
    actual = runner.invoke(
        console, "extract data/datapackage.json --resource-name number-two --yaml"
    )
    expect = extract("data/datapackage.json", name="number-two")
    assert actual.exit_code == 0
    assert yaml.safe_load(actual.stdout) == expect


def test_console_extract_single_resource_csv():
    actual = runner.invoke(
        console, "extract data/datapackage.json --resource-name number-two --csv"
    )
    assert actual.exit_code == 0
    assert (
        json.dumps(actual.stdout, ensure_ascii=False)
        == '"id,name\\n1,中国人\\n2,english\\n"'
    )


def test_extract_resource_from_csv_semicolon_delimiter_1009():
    actual = runner.invoke(
        console,
        'extract data/issue-1009-semicolon.csv --dialect \'{"delimiter": ";"}\' --csv',
    )
    assert actual.exit_code == 0
    assert (
        json.dumps(actual.stdout, ensure_ascii=False)
        == '"fieldNameA,fieldNameB\\n123,c\\n"'
    )


def test_extract_resource_from_csv_semicolon_delimiter_keep_delimiter_1009():
    actual = runner.invoke(
        console,
        'extract data/issue-1009-semicolon.csv --dialect \'{"delimiter": ";"}\' --csv --keep-delimiter',
    )
    assert actual.exit_code == 0
    assert (
        json.dumps(actual.stdout, ensure_ascii=False)
        == '"fieldNameA;fieldNameB\\n123;c\\n"'
    )


def test_extract_resource_from_csv_comma_delimiter_1009():
    actual = runner.invoke(
        console,
        "extract data/issue-1009-comma.csv --csv",
    )
    assert actual.exit_code == 0
    assert (
        json.dumps(actual.stdout, ensure_ascii=False)
        == '"fieldNameA,fieldNameB\\n123,c\\n"'
    )


@pytest.mark.vcr
def test_extract_description_option_issue_1362():
    descriptor = "https://umweltanwendungen.schleswig-holstein.de/pegel/jsp/frictionless.jsp?mstnr=114069&thema=w"
    actual = runner.invoke(
        console, f"extract '{descriptor}' --format json --json --limit-rows 1 --name name"
    )
    print(json.loads(actual.stdout))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout)["name"][0]["Wasserstand"] == 690
