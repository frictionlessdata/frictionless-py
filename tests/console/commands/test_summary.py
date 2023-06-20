import os

import pytest
from typer.testing import CliRunner

from frictionless import platform
from frictionless.console import console

runner = CliRunner()


def test_console_summary_error_not_found():
    result = runner.invoke(console, "summary data/countriess.csv")
    assert result.exit_code == 1
    assert (
        result.stdout.count("[scheme-error]")
        and result.stdout.count("[Errno 2]")
        and result.stdout.count("data/countriess.csv")
    )


def test_console_summary_invalid():
    result = runner.invoke(console, "summary data/countries-invalid.yaml")
    assert result.exit_code == 1
    assert result.stdout.count(
        'Field is not valid: "required" should be set as "constraints.required"'
    )


def test_console_summary():
    result = runner.invoke(console, "summary data/countries.csv")
    assert result.exit_code == 1
    assert result.stdout.count("invalid")
    assert result.stdout.count("Describe")
    assert result.stdout.count("Extract")
    assert result.stdout.count("Validate")
    assert result.stdout.count("Summary")
    assert result.stdout.count("Errors")


def test_console_summary_yaml():
    result = runner.invoke(console, "summary data/countries.yaml")
    assert result.exit_code == 1
    assert result.stdout.count("invalid")
    assert result.stdout.count("Describe")
    assert result.stdout.count("Extract")
    assert result.stdout.count("Validate")
    assert result.stdout.count("Summary")
    assert result.stdout.count("Errors")


def test_console_summary_json():
    result = runner.invoke(console, "summary data/countries.json")
    assert result.exit_code == 1
    assert result.stdout.count("invalid")
    assert result.stdout.count("Describe")
    assert result.stdout.count("Extract")
    assert result.stdout.count("Validate")
    assert result.stdout.count("Summary")
    assert result.stdout.count("Errors")


def test_console_summary_valid():
    result = runner.invoke(console, "summary data/capital-valid.csv")
    assert result.exit_code == 0
    assert result.stdout.count("valid")
    assert result.stdout.count("Describe")
    assert result.stdout.count("Extract")
    assert result.stdout.count("Validate")
    assert result.stdout.count("Summary")
    assert not result.stdout.count("Errors")


def test_console_summary_describe():
    result = runner.invoke(console, "summary data/countries.csv")
    assert result.exit_code == 1
    with open("data/fixtures/summary/describe.txt", encoding="utf-8") as file:
        assert result.stdout.count(file.read().strip())


def test_console_summary_describe_with_required_field():
    result = runner.invoke(console, "summary data/countries.yaml")
    assert result.exit_code == 1
    with open(
        "data/fixtures/summary/describe-with-required-field.txt", encoding="utf-8"
    ) as file:
        assert result.stdout.count(file.read().strip())


def test_console_summary_extract():
    result = runner.invoke(console, "summary data/countries.csv")
    assert result.exit_code == 1
    with open("data/fixtures/summary/extract.txt", encoding="utf-8") as file:
        assert result.stdout.count(file.read().strip())


def test_console_summary_extract_only_5_rows():
    result = runner.invoke(console, "summary data/long.csv")
    assert result.exit_code == 0
    assert result.stdout.count("valid")
    with open("data/fixtures/summary/five-rows-only.txt", encoding="utf-8") as file:
        assert result.stdout.count(file.read().strip())


def test_console_summary_validate():
    result = runner.invoke(console, "summary data/countries.csv")
    assert result.exit_code == 1
    assert result.stdout.count("# invalid:")


def test_console_summary_validate_summary():
    result = runner.invoke(console, "summary data/countries.csv")
    assert result.exit_code == 1
    assert result.stdout.count("| Name         | Value              |")
    assert result.stdout.count("| File Place   | data/countries.csv |")
    assert result.stdout.count("| File Size    | 143 Bytes          |")
    assert result.stdout.count("| Total Time   |")
    assert result.stdout.count("| Rows Checked | 5                  |")
    assert result.stdout.count("| Total Errors | 4                  |")
    assert result.stdout.count("| Extra Cell   | 1                  |")
    assert result.stdout.count("| Missing Cell | 3                  |")


def test_console_summary_validate_errors():
    result = runner.invoke(console, "summary data/countries.csv")
    assert result.exit_code == 1

    # Read
    expected_file_path = "data/fixtures/summary/multiline-errors.txt"
    with open(expected_file_path, encoding="utf-8") as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_summary_without_command(tmpdir):
    output_file_path = f"{tmpdir}/output.txt"
    exit_code = os.system(f"frictionless data/countries.csv > {output_file_path}")
    if platform.type != "windows":
        # A value of 256 means the spawned console terminated with exit code 1
        # https://stackoverflow.com/questions/47832180/os-system-returns-the-value-256-when-run-from-crontab
        assert exit_code == 256
    else:
        assert exit_code == 1
    with open(output_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert (
        expected.count("Describe")
        and expected.count("Extract")
        and expected.count("Validate")
        and expected.count("Summary")
        and expected.count("Errors")
    )


def test_console_summary_without_filepath():
    result = runner.invoke(console, "summary")
    assert result.exit_code == 1
    assert result.stdout.strip() == 'Providing "source" is required'


def test_console_summary_zipped_innerpath():
    result = runner.invoke(console, "summary data/table.csv.zip")
    assert result.exit_code == 0
    assert result.stdout.count("table.csv.zip -> table.csv")
