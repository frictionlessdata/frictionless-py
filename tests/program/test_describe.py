import json
import yaml
import pytest
from typer.testing import CliRunner
from frictionless import program, describe, Dialect, Detector, helpers


runner = CliRunner()


# General


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_program_describe():
    actual = runner.invoke(program, "describe data/table.csv --stats")
    assert actual.exit_code == 0
    assert actual.stdout.count("metadata: data/table.csv")
    assert actual.stdout.count("hash: 6c2c61dd9b0e9c6876139a449ed87933")


def test_program_describe_type_schema():
    actual = runner.invoke(program, "describe data/table.csv --json --type schema")
    expect = describe("data/table.csv", type="schema")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_program_describe_type_dialect():
    actual = runner.invoke(program, "describe data/delimiter.csv --json --type dialect")
    expect = describe("data/delimiter.csv", type="dialect")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_program_describe_header_rows():
    actual = runner.invoke(program, "describe data/table.csv --json --header-rows '1,2'")
    expect = describe("data/table.csv", dialect=Dialect(header_rows=[1, 2]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_program_describe_header_join():
    actual = runner.invoke(
        program,
        "describe data/table.csv --json --header-rows '1,2' --header-join ':'",
    )
    expect = describe(
        "data/table.csv",
        dialect=Dialect(header_rows=[1, 2], header_join=":"),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_program_describe_comment_rows():
    actual = runner.invoke(program, "describe data/table.csv --json --comment-rows 1")
    expect = describe("data/table.csv", dialect=Dialect(comment_rows=[1]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_program_describe_field_type():
    actual = runner.invoke(program, "describe data/table.csv --json --field-type string")
    expect = describe("data/table.csv", detector=Detector(field_type="string"))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_program_describe_field_names():
    actual = runner.invoke(program, "describe data/table.csv --json --field-names 'a,b'")
    expect = describe("data/table.csv", detector=Detector(field_names=["a", "b"]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_program_describe_field_missing_values():
    actual = runner.invoke(
        program,
        "describe data/table.csv --json --field-missing-values 1",
    )
    expect = describe(
        "data/table.csv",
        detector=Detector(field_missing_values=["1"]),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_program_describe_yaml():
    actual = runner.invoke(program, "describe data/table.csv --yaml")
    expect = describe("data/table.csv")
    assert actual.exit_code == 0
    assert yaml.safe_load(actual.stdout) == expect.to_descriptor()


def test_program_describe_json():
    actual = runner.invoke(program, "describe data/table.csv --json")
    expect = describe("data/table.csv")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect.to_descriptor()


def test_program_describe_error_not_found():
    actual = runner.invoke(program, "describe data/bad.csv")
    assert actual.exit_code == 1
    assert (
        actual.stdout.count("[scheme-error]")
        and actual.stdout.count("[Errno 2]")
        and actual.stdout.count("data/bad.csv")
    )


def test_program_describe_basepath():
    result = runner.invoke(program, "describe --basepath data *-3.csv")
    expect = describe("*-3.csv", basepath="data")
    assert result.exit_code == 0
    assert yaml.safe_load(result.stdout) == expect.to_descriptor()


# Bugs


def test_program_describe_package_with_dialect_1126():
    result = runner.invoke(
        program,
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


def test_program_describe_package_with_dialect_path_1126():
    result = runner.invoke(
        program,
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


def test_program_describe_package_with_incorrect_dialect_1126():
    result = runner.invoke(
        program,
        'describe data/country-2.csv --json --dialect \'{"delimiter": ","}\' --type package',
    )
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["resources"][0]["schema"] == {
        "fields": [{"type": "string", "name": "# Author: the scientist"}]
    }


def test_program_describe_package_with_glob_having_one_incorrect_dialect_1126():
    result = runner.invoke(
        program,
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
