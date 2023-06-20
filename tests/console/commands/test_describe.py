import json

import pytest
import yaml
from typer.testing import CliRunner

from frictionless import Detector, Dialect, describe, formats, platform
from frictionless.console import console

runner = CliRunner()


# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_console_describe():
    actual = runner.invoke(console, "describe data/table.csv --stats --yaml")
    assert actual.exit_code == 0
    assert actual.stdout.count(
        "hash: sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    )


def test_console_describe_type_schema():
    actual = runner.invoke(console, "describe data/table.csv --json --type schema")
    expect = describe("data/table.csv", type="schema")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_console_describe_type_dialect():
    actual = runner.invoke(console, "describe data/delimiter.csv --json --type dialect")
    expect = describe("data/delimiter.csv", type="dialect")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_console_describe_header_rows():
    actual = runner.invoke(console, "describe data/table.csv --json --header-rows '1,2'")
    expect = describe("data/table.csv", dialect=Dialect(header_rows=[1, 2]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_console_describe_header_join():
    actual = runner.invoke(
        console,
        "describe data/table.csv --json --header-rows '1,2' --header-join ':'",
    )
    expect = describe(
        "data/table.csv",
        dialect=Dialect(header_rows=[1, 2], header_join=":"),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_console_describe_comment_rows():
    actual = runner.invoke(console, "describe data/table.csv --json --comment-rows 1")
    expect = describe("data/table.csv", dialect=Dialect(comment_rows=[1]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_console_describe_field_type():
    actual = runner.invoke(console, "describe data/table.csv --json --field-type string")
    expect = describe("data/table.csv", detector=Detector(field_type="string"))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_console_describe_field_names():
    actual = runner.invoke(console, "describe data/table.csv --json --field-names 'a,b'")
    expect = describe("data/table.csv", detector=Detector(field_names=["a", "b"]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_console_describe_field_missing_values():
    actual = runner.invoke(
        console,
        "describe data/table.csv --json --field-missing-values 1",
    )
    expect = describe(
        "data/table.csv",
        detector=Detector(field_missing_values=["1"]),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_console_describe_yaml():
    actual = runner.invoke(console, "describe data/table.csv --yaml")
    expect = describe("data/table.csv")
    assert actual.exit_code == 0
    assert yaml.safe_load(actual.stdout) == expect.to_descriptor()


def test_console_describe_json():
    actual = runner.invoke(console, "describe data/table.csv --json")
    expect = describe("data/table.csv")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_console_describe_error_not_found():
    actual = runner.invoke(console, "describe data/bad.csv")
    assert actual.exit_code == 1
    assert actual.stdout.count("[Errno 2]")
    assert actual.stdout.count("data/bad.csv")


def test_console_describe_basepath():
    result = runner.invoke(console, "describe --basepath data *-3.csv --yaml")
    expect = describe("*-3.csv", basepath="data")
    assert result.exit_code == 0
    assert yaml.safe_load(result.stdout) == expect.to_descriptor()


def test_console_describe_extract_dialect_sheet_option():
    actual = runner.invoke(console, "describe data/sheet2.xls --sheet Sheet2 --json")
    expect = describe("data/sheet2.xls", control=formats.ExcelControl(sheet="Sheet2"))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_console_describe_extract_dialect_table_option_sql(sqlite_url_data):
    actual = runner.invoke(console, f"describe {sqlite_url_data} --table fruits --json")
    expect = describe(sqlite_url_data, control=formats.SqlControl(table="fruits"))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


# Bugs


def test_console_describe_package_with_dialect_1126():
    result = runner.invoke(
        console,
        'describe data/country-2.csv --json --dialect \'{"delimiter": ";"}\' --type package',
    )
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["resources"][0]["schema"] == {
        "fields": [
            {"type": "integer", "name": "id"},
            {"type": "integer", "name": "neighbor_id"},
            {"type": "string", "name": "name"},
            {"type": "integer", "name": "population"},
        ]
    }


def test_console_describe_package_with_dialect_path_1126():
    result = runner.invoke(
        console,
        "describe data/country-2.csv --json --dialect data/dialect.json --type package",
    )
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["resources"][0]["schema"] == {
        "fields": [
            {"type": "integer", "name": "id"},
            {"type": "integer", "name": "neighbor_id"},
            {"type": "string", "name": "name"},
            {"type": "integer", "name": "population"},
        ]
    }


def test_console_describe_package_with_incorrect_dialect_1126():
    result = runner.invoke(
        console,
        'describe data/country-2.csv --json --dialect \'{"delimiter": ","}\' --type package',
    )
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["resources"][0]["schema"] == {
        "fields": [{"type": "string", "name": "# Author: the scientist"}]
    }


def test_console_describe_package_with_glob_having_one_incorrect_dialect_1126():
    result = runner.invoke(
        console,
        'describe data/country-*.csv --json --dialect \'{"delimiter": ","}\' --type package',
    )
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["resources"][0]["schema"] == {
        "fields": [
            {"type": "integer", "name": "id"},
            {"type": "integer", "name": "neighbor_id"},
            {"type": "string", "name": "name"},
            {"type": "integer", "name": "population"},
        ]
    }
    assert output["resources"][1]["schema"] == {
        "fields": [{"type": "string", "name": "# Author: the scientist"}]
    }
