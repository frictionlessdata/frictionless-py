import json

import pytest
import yaml
from typer.testing import CliRunner

from frictionless import Detector, Dialect, platform, validate
from frictionless.console import console

runner = CliRunner()


# General


def test_console_validate():
    actual = runner.invoke(console, "validate data/table.csv")
    assert actual.exit_code == 0
    assert actual.stdout.count("data/table.csv")
    assert actual.stdout.count("VALID")


def test_console_validate_invalid():
    actual = runner.invoke(console, "validate data/invalid.csv")
    assert actual.exit_code == 1
    assert actual.stdout.count("data/invalid.csv")
    assert actual.stdout.count("INVALID")


def test_console_validate_header_rows():
    actual = runner.invoke(console, "validate data/table.csv --json --header-rows '1,2'")
    expect = validate("data/table.csv", dialect=Dialect(header_rows=[1, 2]))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_header_join():
    actual = runner.invoke(
        console,
        "validate data/table.csv --json --header-rows '1,2' --header-join ':'",
    )
    expect = validate(
        "data/table.csv",
        dialect=Dialect(header_rows=[1, 2], header_join=":"),
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_comment_rows():
    actual = runner.invoke(console, "validate data/table.csv --json --comment-rows 1")
    expect = validate("data/table.csv", dialect=Dialect(comment_rows=[1]))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_field_type():
    actual = runner.invoke(console, "validate data/table.csv --json --field-type string")
    expect = validate("data/table.csv", detector=Detector(field_type="string"))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_field_names():
    actual = runner.invoke(console, "validate data/table.csv --json --field-names 'a,b'")
    expect = validate("data/table.csv", detector=Detector(field_names=["a", "b"]))
    assert actual.exit_code == 1
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_field_missing_values():
    actual = runner.invoke(
        console,
        "validate data/table.csv --json --field-missing-values 1",
    )
    expect = validate(
        "data/table.csv",
        detector=Detector(field_missing_values=["1"]),
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_console_validate_chucksum_hash():
    actual = runner.invoke(
        console,
        "validate data/table.csv --json --hash 6c2c61dd9b0e9c6876139a449ed87933",
    )
    expect = validate(
        "data/table.csv",
        hash="6c2c61dd9b0e9c6876139a449ed87933",
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_console_validate_chucksum_bytes():
    actual = runner.invoke(console, "validate data/table.csv --json --bytes 30")
    expect = validate("data/table.csv", bytes=30)
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_chucksum_rows():
    actual = runner.invoke(console, "validate data/table.csv --json --rows 2")
    expect = validate("data/table.csv", rows=2)
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_pick_errors():
    actual = runner.invoke(
        console,
        "validate data/table.csv --json --pick-errors 'blank-row,extra-cell'",
    )
    expect = validate(
        "data/table.csv",
        pick_errors=["blank-row", "extra-cell"],
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_skip_errors():
    actual = runner.invoke(
        console,
        "validate data/table.csv --json --skip-errors 'blank-row,extra-cell'",
    )
    expect = validate(
        "data/table.csv",
        skip_errors=["blank-row", "extra-cell"],
    )
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_limit_errors():
    actual = runner.invoke(console, "validate data/table.csv --json --limit-errors 1")
    expect = validate("data/table.csv", limit_errors=1)
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_yaml():
    actual = runner.invoke(console, "validate data/table.csv --yaml")
    expect = validate("data/table.csv")
    assert actual.exit_code == 0
    assert no_time(yaml.safe_load(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_json():
    actual = runner.invoke(console, "validate data/table.csv --json")
    expect = validate("data/table.csv")
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


def test_console_validate_error_not_found():
    actual = runner.invoke(console, "validate data/bad.csv")
    assert actual.exit_code == 1
    assert actual.stdout.count("[Errno 2]")
    assert actual.stdout.count("data/bad.csv")


@pytest.mark.skip
def test_console_validate_summary():
    actual = runner.invoke(console, "validate data/datapackage.json --type resource")
    assert actual.exit_code == 1
    assert actual.stdout.count(
        'The data resource has an error: one of the properties "path" or "data" is required'
    )


def test_console_validate_schema_sync():
    actual = runner.invoke(
        console,
        "validate data/resource-sync.json --json --schema-sync",
    )
    expect = validate("data/resource-sync.json", detector=Detector(schema_sync=True))
    assert actual.exit_code == 0
    assert no_time(json.loads(actual.stdout)) == no_time(expect.to_descriptor())


# Bugs


def test_console_validate_zipped_resources_979():
    actual = runner.invoke(
        console, "validate data/zipped-resources/datapackage.json --yaml"
    )
    assert actual.exit_code == 1
    assert actual.stdout.count("Schema is not valid: names of the fields are not unique")


@pytest.mark.skip
def test_console_validate_long_error_messages_976():
    actual = runner.invoke(console, "validate data/datapackage.json --type resource")
    assert actual.exit_code == 1
    expected_file_path = "data/fixtures/cli/long-error-messages-976.txt"
    with open(expected_file_path, encoding="utf-8") as file:
        assert actual.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_validate_partial_validation_info_933():
    actual = runner.invoke(console, "validate data/countries.csv --limit-errors 2")
    assert actual.exit_code == 1
    assert actual.stdout.count("reached error limit: 2")


def test_console_validate_single_resource_221():
    actual = runner.invoke(
        console, "validate data/datapackage.json --resource-name number-two"
    )
    assert actual.exit_code == 0
    assert actual.stdout.count("table-reverse.csv")
    assert actual.stdout.count("VALID")


def test_console_validate_single_invalid_resource_221():
    actual = runner.invoke(
        console, "validate data/datapackage.json --resource-name number-twoo"
    )
    assert actual.exit_code == 1
    assert actual.stdout.count("number-twoo")


def test_console_validate_multipart_resource_1140():
    actual = runner.invoke(console, "validate data/multipart.package.json")
    assert actual.exit_code == 0
    assert actual.stdout.count("chunk1.csv (multipart)")
    assert actual.stdout.count("VALID")


@pytest.mark.skip(reason="issue-1215")
def test_console_validate_multipart_zipped_resource_1140():
    actual = runner.invoke(console, "validate data/multipart-zipped.package.json")
    assert actual.exit_code == 0
    assert actual.stdout.count("chunk1.csv.zip,chunk2.csv.zip")


def test_console_validate_enforce_required_fields_only_for_data_using_schema_sync_1258():
    actual = runner.invoke(
        console,
        "validate data/issue-1258.json --schema-sync --json",
    )
    output = json.loads(actual.stdout)
    expect = [error for error in output["tasks"][0]["errors"]]
    # using schema-sync to skip type-error due to positional matching of
    # fields and data, incase any field data is missing
    assert "type-error" not in expect
    assert "incorrect-label" not in expect


def test_console_validate_dialect_overrided_issue_1478():
    actual = runner.invoke(console, "validate data/issue-1478/resource.json")
    assert actual.exit_code == 0


def test_console_validate_inquiry():
    actual = runner.invoke(console, "validate data/inquiry.yaml")
    assert actual.exit_code == 1
    assert actual.stdout.count("data/capital-valid.csv")
    assert actual.stdout.count("data/capital-invalid.csv")


# Helpers


def no_time(descriptor):
    for task in descriptor.get("tasks", []):
        task["stats"].pop("seconds", None)
    descriptor["stats"].pop("seconds", None)
    return descriptor
