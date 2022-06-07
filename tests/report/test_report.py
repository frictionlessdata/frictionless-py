from frictionless import validate


def test_report_summary():
    report = validate("data/countries.csv")
    output = report.to_summary()
    assert output.count("invalid") and output.count("Summary") and output.count("Errors")


def test_report_summary_validate_summary():
    report = validate("data/countries.csv")
    output = report.to_summary()
    assert (
        output.count("File name                   |")
        and output.count("File size (bytes)           | 143")
        and output.count("Total Time Taken (sec)      |")
        and output.count("Total Errors                | 4")
        and output.count("Extra Cell (extra-cell)     | 1")
        and output.count("Missing Cell (missing-cell) | 3")
    )


def test_report_summary_validate_errors():
    report = validate("data/countries.csv")
    output = report.to_summary()
    with open("data/fixtures/program/summary/errors.txt", encoding="utf-8") as file:
        expected = file.read()
    assert output.count(expected.strip())


def test_report_summary_valid():
    report = validate("data/capital-valid.csv")
    output = report.to_summary()
    assert (
        output.count("valid") and output.count("Summary") and not output.count("Errors")
    )
