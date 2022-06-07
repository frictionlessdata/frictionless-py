from frictionless import validate


def test_report_task_error_not_found():
    report = validate("data/countriess.csv")
    assert (
        report.tasks[0].errors[0].code == "scheme-error"
        and report.tasks[0].errors[0].description
        == "Data reading error because of incorrect scheme."
    )


def test_report_task_summary():
    report = validate("data/countries.csv")
    assert report.valid is False and ["describe", "extract", "validate"] == list(
        report.tasks[0].to_summary().keys()
    )


def test_report_task_summary_valid():
    report = validate("data/capital-valid.csv")
    assert report.valid is True and ["summary"] == list(
        report.tasks[0].to_summary()["validate"].keys()
    )


def test_report_task_summary_describe():
    report = validate("data/countries.csv")
    output = report.tasks[0].to_summary()["describe"]
    assert (
        output.count("| id          | integer |            |")
        and output.count("| neighbor_id | string  |            |")
        and output.count("| name        | string  |            |")
        and output.count("| population  | string  |            |")
    )


def test_report_task_summary_extract():
    report = validate("data/countries.csv")
    output = report.tasks[0].to_summary()["extract"]
    assert (
        output.count("|  1 | 'Ireland'   | 'Britain' | '67'       |")
        and output.count("|  2 | '3'         | 'France'  | 'n/a'      |")
        and output.count("|  3 | '22'        | 'Germany' | '83'       |")
        and output.count("|  4 | None        | 'Italy'   | '60'       |")
        and output.count("|  5 | None        | None      | None       |")
    )


def test_report_task_summary_extract_only_5_rows():
    report = validate("data/long.csv")
    output = report.tasks[0].to_summary()["extract"]
    assert (
        output.count("|  1 | 'a'  |")
        and output.count("|  2 | 'b'  |")
        and output.count("|  3 | 'c'  |")
        and output.count("|  4 | 'd'  |")
        and output.count("|  5 | 'e'  |")
        and not output.count("|  6 | 'f'  |")
    )


def test_report_task_summary_validate_summary():
    report = validate("data/countries.csv")
    validate_summary = report.tasks[0].to_summary()["validate"]["summary"]
    assert (
        validate_summary.count("File name                   |")
        and validate_summary.count("File size (bytes)           | 143")
        and validate_summary.count("Total Time Taken (sec)      |")
        and validate_summary.count("Total Errors                | 4")
        and validate_summary.count("Extra Cell (extra-cell)     | 1")
        and validate_summary.count("Missing Cell (missing-cell) | 3")
    )


def test_report_task_summary_validate_errors():
    report = validate("data/countries.csv")
    output_file_path = "data/fixtures/program/summary/errors.txt"
    with open(output_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert report.tasks[0].to_summary()["validate"]["errors"] == expected.strip()
