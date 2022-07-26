import json
import yaml
import pytest
from typer.testing import CliRunner
from frictionless import Detector, Dialect, Stats, validate, platform
from frictionless.program import program

runner = CliRunner()


# General


def test_program_validate():
    actual = runner.invoke(program, "validate data/table.csv")
    assert actual.exit_code == 0
    assert actual.stdout.count("valid: data/table.csv")


def test_program_validate_invalid():
    actual = runner.invoke(program, "validate data/invalid.csv")
    assert actual.exit_code == 1
    assert actual.stdout.count("invalid: data/invalid.csv")


def test_program_validate_header_rows():
    actual = runner.invoke(program, "validate data/table.csv --json --header-rows '1,2'")
    expect = validate("data/table.csv", dialect=Dialect(header_rows=[1, 2]))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_header_join():
    actual = runner.invoke(
        program,
        "validate data/table.csv --json --header-rows '1,2' --header-join ':'",
    )
    expect = validate(
        "data/table.csv",
        dialect=Dialect(header_rows=[1, 2], header_join=":"),
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_comment_rows():
    actual = runner.invoke(program, "validate data/table.csv --json --comment-rows 1")
    expect = validate("data/table.csv", dialect=Dialect(comment_rows=[1]))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_field_type():
    actual = runner.invoke(program, "validate data/table.csv --json --field-type string")
    expect = validate("data/table.csv", detector=Detector(field_type="string"))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_field_names():
    actual = runner.invoke(program, "validate data/table.csv --json --field-names 'a,b'")
    expect = validate("data/table.csv", detector=Detector(field_names=["a", "b"]))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_field_missing_values():
    actual = runner.invoke(
        program,
        "validate data/table.csv --json --field-missing-values 1",
    )
    expect = validate(
        "data/table.csv",
        detector=Detector(field_missing_values=["1"]),
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_program_validate_chucksum_hash():
    actual = runner.invoke(
        program,
        "validate data/table.csv --json --stats-md5 6c2c61dd9b0e9c6876139a449ed87933",
    )
    expect = validate(
        "data/table.csv",
        stats=Stats(md5="6c2c61dd9b0e9c6876139a449ed87933"),
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_program_validate_chucksum_bytes():
    actual = runner.invoke(program, "validate data/table.csv --json --stats-bytes 30")
    expect = validate("data/table.csv", stats=Stats(bytes=30))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_chucksum_rows():
    actual = runner.invoke(program, "validate data/table.csv --json --stats-rows 2")
    expect = validate("data/table.csv", stats=Stats(rows=2))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_pick_errors():
    actual = runner.invoke(
        program,
        "validate data/table.csv --json --pick-errors 'blank-row,extra-cell'",
    )
    expect = validate(
        "data/table.csv",
        pick_errors=["blank-row", "extra-cell"],
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_skip_errors():
    actual = runner.invoke(
        program,
        "validate data/table.csv --json --skip-errors 'blank-row,extra-cell'",
    )
    expect = validate(
        "data/table.csv",
        skip_errors=["blank-row", "extra-cell"],
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_limit_errors():
    actual = runner.invoke(program, "validate data/table.csv --json --limit-errors 1")
    expect = validate("data/table.csv", limit_errors=1)
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_yaml():
    actual = runner.invoke(program, "validate data/table.csv --yaml")
    expect = validate("data/table.csv")
    assert actual.exit_code == 0
    assert no_time(yaml.safe_load(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_json():
    actual = runner.invoke(program, "validate data/table.csv --json")
    expect = validate("data/table.csv")
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_program_validate_error_not_found():
    actual = runner.invoke(program, "validate data/bad.csv")
    assert actual.exit_code == 1
    assert actual.stdout.count("[Errno 2]")
    assert actual.stdout.count("data/bad.csv")


def test_program_validate_summary():
    actual = runner.invoke(program, "validate data/datapackage.json --type resource")
    assert actual.exit_code == 1
    assert actual.stdout.count("Summary")
    assert actual.stdout.count("File Place")
    assert actual.stdout.count("File Size")
    assert actual.stdout.count("Total Time")


# Bugs


def test_program_validate_zipped_resources_979():
    actual = runner.invoke(program, "validate data/zipped-resources/datapackage.json")
    assert actual.exit_code == 1

    # Read
    expected_file_path = "data/fixtures/cli/zipped-resources-979.txt"
    with open(expected_file_path, encoding="utf-8") as file:
        assert actual.stdout.count(file.read().strip())
    assert actual.stdout.count("valid: ogd10_energieforschungstatistik_ch.csv")
    assert actual.stdout.count("valid: ogd10_catalogs.zip -> finanzquellen.csv")
    assert actual.stdout.count("invalid: ogd10_catalogs.zip -> capital-invalid.csv")


def test_program_validate_long_error_messages_976():
    actual = runner.invoke(program, "validate data/datapackage.json --type resource")
    assert actual.exit_code == 1

    # Read
    expected_file_path = "data/fixtures/cli/long-error-messages-976.txt"
    with open(expected_file_path, encoding="utf-8") as file:
        assert actual.stdout.count(file.read().strip())


def test_program_validate_partial_validation_info_933():
    actual = runner.invoke(program, "validate data/countries.csv --limit-errors 2")
    assert actual.exit_code == 1
    assert actual.stdout.count("reached error limit: 2")


def test_program_validate_single_resource_221():
    actual = runner.invoke(
        program, "validate data/datapackage.json --resource-name number-two"
    )
    assert actual.exit_code == 0
    assert actual.stdout.count("valid: table-reverse.csv")


@pytest.mark.xfail(reason="issue-1205")
def test_program_validate_single_invalid_resource_221():
    actual = runner.invoke(
        program, "validate data/datapackage.json --resource-name number-twoo"
    )
    assert actual.exit_code == 1
    assert actual.stdout.count("invalid: data/datapackage.json")


@pytest.mark.xfail(reason="issue-1205")
def test_program_validate_multipart_resource_1140():
    actual = runner.invoke(program, "validate data/multipart.package.json")
    assert actual.exit_code == 0
    assert actual.stdout.count("chunk1.csv,chunk2.csv")


@pytest.mark.xfail(reason="issue-1205")
def test_program_validate_multipart_zipped_resource_1140():
    actual = runner.invoke(program, "validate data/multipart-zipped.package.json")
    assert actual.exit_code == 0
    assert actual.stdout.count("chunk1.csv.zip,chunk2.csv.zip")


# Helpers


def no_time(descriptor):
    for task in descriptor.get("tasks", []):
        task["stats"].pop("seconds", None)
    descriptor["stats"].pop("seconds", None)
    return descriptor
