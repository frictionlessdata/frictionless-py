import json
import yaml
from typer.testing import CliRunner
from frictionless import program, describe, Detector, helpers


runner = CliRunner()
IS_UNIX = not helpers.is_platform("windows")


# General


def test_program_describe():
    result = runner.invoke(program, "describe data/table.csv --stats")
    assert result.exit_code == 0
    if IS_UNIX:
        assert result.stdout.count("metadata: data/table.csv")
        assert result.stdout.count("hash: 6c2c61dd9b0e9c6876139a449ed87933")


def test_program_describe_type_schema():
    result = runner.invoke(program, "describe data/table.csv --json --type schema")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe("data/table.csv", type="schema")


def test_program_describe_type_dialect():
    result = runner.invoke(program, "describe data/delimiter.csv --json --type dialect")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe("data/delimiter.csv", type="dialect")


def test_program_describe_header_rows():
    result = runner.invoke(program, "describe data/table.csv --json --header-rows '1,2'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"headerRows": [1, 2]}
    )


def test_program_describe_header_join():
    result = runner.invoke(
        program, "describe data/table.csv --json --header-rows '1,2' --header-join ':'"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"headerRows": [1, 2], "headerJoin": ":"}
    )


def test_program_describe_pick_fields():
    result = runner.invoke(program, "describe data/table.csv --json --pick-fields 'id'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"pickFields": ["id"]}
    )


def test_program_describe_skip_fields():
    result = runner.invoke(program, "describe data/table.csv --json --skip-fields 'id'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"skipFields": ["id"]}
    )


def test_program_describe_limit_fields():
    result = runner.invoke(program, "describe data/table.csv --json --limit-fields 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"limitFields": 1}
    )


def test_program_describe_offset_fields():
    result = runner.invoke(program, "describe data/table.csv --json --offset-fields 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"offsetFields": 1}
    )


def test_program_describe_pick_rows():
    result = runner.invoke(program, "describe data/table.csv --json --pick-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"pickRows": [1]}
    )


def test_program_describe_skip_rows():
    result = runner.invoke(program, "describe data/table.csv --json --skip-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"skipRows": [1]}
    )


def test_program_describe_limit_rows():
    result = runner.invoke(program, "describe data/table.csv --json --limit-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"limitRows": 1}
    )


def test_program_describe_offset_rows():
    result = runner.invoke(program, "describe data/table.csv --json --offset-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", layout={"offsetRows": 1}
    )


def test_program_describe_infer_type():
    result = runner.invoke(program, "describe data/table.csv --json --field-type string")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", detector=Detector(field_type="string")
    )


def test_program_describe_infer_names():
    result = runner.invoke(program, "describe data/table.csv --json --field-names 'a,b'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", detector=Detector(field_names=["a", "b"])
    )


def test_program_describe_infer_missing_values():
    result = runner.invoke(
        program, "describe data/table.csv --json --field-missing-values 1"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe(
        "data/table.csv", detector=Detector(field_missing_values=["1"])
    )


def test_program_describe_expand():
    result = runner.invoke(program, "describe data/table.csv --json --expand")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe("data/table.csv", expand=True)


def test_program_describe_yaml():
    result = runner.invoke(program, "describe data/table.csv --yaml")
    assert result.exit_code == 0
    assert yaml.safe_load(result.stdout) == describe("data/table.csv")


def test_program_describe_json():
    result = runner.invoke(program, "describe data/table.csv --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == describe("data/table.csv")


def test_program_describe_error_not_found():
    result = runner.invoke(program, "describe data/bad.csv")
    assert result.exit_code == 1
    assert result.stdout.count("No such file or directory: 'data/bad.csv'")

def test_program_describe_basepath():
    result = runner.invoke(program, "describe --basepath data *-3.csv")
    assert result.exit_code == 0
    assert yaml.safe_load(result.stdout) == describe("*-3.csv", basepath="data")
