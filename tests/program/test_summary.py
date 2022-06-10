import os
from typer.testing import CliRunner
from frictionless import program, helpers

runner = CliRunner()
IS_UNIX = not helpers.is_platform("windows")


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
    assert (
        result.stdout.count("invalid")
        and result.stdout.count("Describe")
        and result.stdout.count("Extract")
        and result.stdout.count("Validate")
        and result.stdout.count("Summary")
        and result.stdout.count("Errors")
    )


def test_program_summary_valid():
    result = runner.invoke(program, "summary data/capital-valid.csv")
    assert result.exit_code == 0
    assert (
        result.stdout.count("valid")
        and result.stdout.count("Describe")
        and result.stdout.count("Extract")
        and result.stdout.count("Validate")
        and result.stdout.count("Summary")
        and not result.stdout.count("Errors")
    )


def test_program_summary_describe():
    result = runner.invoke(program, "summary data/countries.csv")
    assert result.exit_code == 1
    assert (
        result.stdout.count("| name        | type    | required   |")
        and result.stdout.count("| id          | integer |            |")
        and result.stdout.count("| neighbor_id | string  |            |")
        and result.stdout.count("| name        | string  |            |")
        and result.stdout.count("| population  | string  |            |")
    )


def test_program_summary_extract():
    result = runner.invoke(program, "summary data/countries.csv")
    assert result.exit_code == 1
    assert (
        result.stdout.count("| id | neighbor_id | name      | population |")
        and result.stdout.count("|  1 | 'Ireland'   | 'Britain' | '67'       |")
        and result.stdout.count("|  2 | '3'         | 'France'  | 'n/a'      |")
        and result.stdout.count("|  3 | '22'        | 'Germany' | '83'       |")
        and result.stdout.count("|  4 | None        | 'Italy'   | '60'       |")
        and result.stdout.count("|  5 | None        | None      | None       |")
    )


def test_program_summary_extract_only_5_rows():
    result = runner.invoke(program, "summary data/long.csv")
    assert result.exit_code == 0
    assert (
        result.stdout.count("valid")
        and result.stdout.count("|  1 | 'a'  |")
        and result.stdout.count("|  2 | 'b'  |")
        and result.stdout.count("|  3 | 'c'  |")
        and result.stdout.count("|  4 | 'd'  |")
        and result.stdout.count("|  5 | 'e'  |")
        and not result.stdout.count("|  6 | 'f'  |")
    )


def test_program_summary_validate():
    result = runner.invoke(program, "summary data/countries.csv")
    assert result.exit_code == 1
    assert result.stdout.count("# invalid:")


def test_program_summary_validate_summary():
    result = runner.invoke(program, "summary data/countries.csv")
    assert result.exit_code == 1
    assert (
        result.stdout.count("Description                 | Size/Name/Count")
        and result.stdout.count("File name                   | data/countries.csv")
        and result.stdout.count("File size (bytes)           | 143")
        and result.stdout.count("Total Time Taken (sec)      |")
        and result.stdout.count("Total Errors                | 4")
        and result.stdout.count("Extra Cell (extra-cell)     | 1")
        and result.stdout.count("Missing Cell (missing-cell) | 3")
    )


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
    if IS_UNIX:
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
    assert result.stdout.count("table.csv.zip => table.csv")
