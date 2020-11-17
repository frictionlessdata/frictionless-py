import json
import yaml
from typer.testing import CliRunner
from frictionless import Metadata, program, validate

runner = CliRunner()


# General


def test_validate():
    result = runner.invoke(program, "validate data/table.csv")
    assert result.exit_code == 0
    assert result.stdout.count("valid: data/table.csv")


def test_validate_invalid():
    result = runner.invoke(program, "validate data/invalid.csv")
    assert result.exit_code == 1
    assert result.stdout.count("invalid: data/invalid.csv")


def test_validate_header_rows():
    result = runner.invoke(program, "validate data/table.csv --json --header-rows '1,2'")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", dialect={"headerRows": [1, 2]})
    )


def test_validate_header_join():
    result = runner.invoke(
        program, "validate data/table.csv --json --header-rows '1,2' --header-join ':'"
    )
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", dialect={"headerRows": [1, 2], "headerJoin": ":"})
    )


def test_validate_pick_fields():
    result = runner.invoke(program, "validate data/table.csv --json --pick-fields 'id'")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", query={"pickFields": ["id"]})
    )


def test_validate_skip_fields():
    result = runner.invoke(program, "validate data/table.csv --json --skip-fields 'id'")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", query={"skipFields": ["id"]})
    )


def test_validate_limit_fields():
    result = runner.invoke(program, "validate data/table.csv --json --limit-fields 1")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", query={"limitFields": 1})
    )


def test_validate_offset_fields():
    result = runner.invoke(program, "validate data/table.csv --json --offset-fields 1")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", query={"offsetFields": 1})
    )


def test_validate_pick_rows():
    result = runner.invoke(program, "validate data/table.csv --json --pick-rows 1")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", query={"pickRows": [1]})
    )


def test_validate_skip_rows():
    result = runner.invoke(program, "validate data/table.csv --json --skip-rows 1")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", query={"skipRows": [1]})
    )


def test_validate_limit_rows():
    result = runner.invoke(program, "validate data/table.csv --json --limit-rows 1")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", query={"limitRows": 1})
    )


def test_validate_offset_rows():
    result = runner.invoke(program, "validate data/table.csv --json --offset-rows 1")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", query={"offsetRows": 1})
    )


def test_validate_infer_type():
    result = runner.invoke(program, "validate data/table.csv --json --infer-type string")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", infer_type="string")
    )


def test_validate_infer_names():
    result = runner.invoke(program, "validate data/table.csv --json --infer-names 'a,b'")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", infer_names=["a", "b"])
    )


def test_validate_infer_missing_values():
    result = runner.invoke(
        program, "validate data/table.csv --json --infer-missing-values 1"
    )
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", infer_missing_values=["1"])
    )


def test_validate_chucksum_hash():
    result = runner.invoke(
        program,
        "validate data/table.csv --json --checksum-hash 6c2c61dd9b0e9c6876139a449ed87933",
    )
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", checksum={"hash": "6c2c61dd9b0e9c6876139a449ed87933"})
    )


def test_validate_chucksum_bytes():
    result = runner.invoke(
        program,
        "validate data/table.csv --json --checksum-bytes 30",
    )
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", checksum={"bytes": 30})
    )


def test_validate_chucksum_rows():
    result = runner.invoke(
        program,
        "validate data/table.csv --json --checksum-rows 2",
    )
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", checksum={"rows": 2})
    )


def test_validate_pick_errors():
    result = runner.invoke(
        program,
        "validate data/table.csv --json --pick-errors 'blank-row,extra-cell'",
    )
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", pick_errors=["blank-row", "extra-cell"])
    )


def test_validate_skip_errors():
    result = runner.invoke(
        program,
        "validate data/table.csv --json --skip-errors 'blank-row,extra-cell'",
    )
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", skip_errors=["blank-row", "extra-cell"])
    )


def test_validate_limit_errors():
    result = runner.invoke(
        program,
        "validate data/table.csv --json --limit-errors 1",
    )
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(
        validate("data/table.csv", limit_errors=1)
    )


def test_validate_yaml():
    result = runner.invoke(program, "validate data/table.csv --yaml")
    assert result.exit_code == 0
    assert no_time(yaml.load(result.stdout)) == no_time(validate("data/table.csv"))


def test_validate_json():
    result = runner.invoke(program, "validate data/table.csv --json")
    assert result.exit_code == 0
    assert no_time(json.loads(result.stdout)) == no_time(validate("data/table.csv"))


def test_validate_error_not_found():
    result = runner.invoke(program, "validate data/bad.csv")
    assert result.exit_code == 1
    assert result.stdout.count("No such file or directory: 'data/bad.csv'")


# Helpers


def no_time(descriptor):
    if isinstance(descriptor, Metadata):
        descriptor = descriptor.to_dict()
    for table in descriptor.get("tables", []):
        table.pop("time", None)
    descriptor.pop("time", None)
    return descriptor
