import os
import pytest
from typer.testing import CliRunner
from frictionless import program, helpers

runner = CliRunner()


def test_program_summary_error_not_found():
    result = runner.invoke(program, "summary data/countriess.csv")
    assert result.exit_code == 1
    assert (
        result.stdout.count("[scheme-error]")
        and result.stdout.count("[Errno 2]")
        and result.stdout.count("data/countriess.csv")
    )


def test_program_summary():
    result = runner.invoke(program, "summary data/countries.csv")
    assert result.exit_code == 1
    assert result.stdout.count("invalid")
    assert result.stdout.count("Describe")
    assert result.stdout.count("Extract")
    assert result.stdout.count("Validate")
    assert result.stdout.count("Summary")
    assert result.stdout.count("Errors")


def test_program_summary_valid():
    result = runner.invoke(program, "summary data/capital-valid.csv")
    assert result.exit_code == 0
    assert result.stdout.count("valid")
    assert result.stdout.count("Describe")
    assert result.stdout.count("Extract")
    assert result.stdout.count("Validate")
    assert result.stdout.count("Summary")
    assert not result.stdout.count("Errors")


def test_program_summary_describe():
    result = runner.invoke(program, "summary data/countries.csv")
    assert result.exit_code == 1
    assert result.stdout.count("| name        | type    | required   |")
    assert result.stdout.count("| id          | integer |            |")
    assert result.stdout.count("| neighbor_id | string  |            |")
    assert result.stdout.count("| name        | string  |            |")
    assert result.stdout.count("| population  | string  |            |")


def test_program_summary_extract():
    result = runner.invoke(program, "summary data/countries.csv")
    assert result.exit_code == 1
    assert result.stdout.count("| id | neighbor_id | name      | population |")
    assert result.stdout.count("|  1 | 'Ireland'   | 'Britain' | '67'       |")
    assert result.stdout.count("|  2 | '3'         | 'France'  | 'n/a'      |")
    assert result.stdout.count("|  3 | '22'        | 'Germany' | '83'       |")
    assert result.stdout.count("|  4 | None        | 'Italy'   | '60'       |")
    assert result.stdout.count("|  5 | None        | None      | None       |")


def test_program_summary_extract_only_5_rows():
    result = runner.invoke(program, "summary data/long.csv")
    assert result.exit_code == 0
    assert result.stdout.count("valid")
    assert result.stdout.count("|  1 | 'a'  |")
    assert result.stdout.count("|  2 | 'b'  |")
    assert result.stdout.count("|  3 | 'c'  |")
    assert result.stdout.count("|  4 | 'd'  |")
    assert result.stdout.count("|  5 | 'e'  |")
    assert not result.stdout.count("|  6 | 'f'  |")


def test_program_summary_validate():
    result = runner.invoke(program, "summary data/countries.csv")
    assert result.exit_code == 1
    assert result.stdout.count("# invalid:")


@pytest.mark.xfail(reason="Update")
def test_program_summary_validate_summary():
    result = runner.invoke(program, "summary data/countries.csv")
    assert result.exit_code == 1
    assert result.stdout.count("Description                 | Size/Name/Count")
    assert result.stdout.count("File name                   | data/countries.csv")
    assert result.stdout.count("File size (bytes)           | 143")
    assert result.stdout.count("Total Time Taken (sec)      |")
    assert result.stdout.count("Total Errors                | 4")
    assert result.stdout.count("Extra Cell (extra-cell)     | 1")
    assert result.stdout.count("Missing Cell (missing-cell) | 3")


def test_program_summary_validate_errors():
    result = runner.invoke(program, "summary data/countries.csv")
    output_file_path = "data/fixtures/summary/multiline-errors.txt"
    with open(output_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert result.exit_code == 1
    assert result.stdout.count(expected.strip())


def test_program_summary_without_command(tmpdir):
    output_file_path = f"{tmpdir}/output.txt"
    exit_code = os.system(f"frictionless data/countries.csv > {output_file_path}")
    if not helpers.is_platform("windows"):
        # A value of 256 means the spawned program terminated with exit code 1
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


def test_program_summary_without_filepath():
    result = runner.invoke(program, "summary")
    assert result.exit_code == 1
    assert result.stdout.strip() == 'Providing "source" is required'


def test_program_summary_zipped_innerpath():
    result = runner.invoke(program, "summary data/table.csv.zip")
    assert result.exit_code == 0
    assert result.stdout.count("table.csv.zip -> table.csv")
