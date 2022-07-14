from frictionless import validate, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_program_error_not_found():
    report = validate("data/countriess.csv")
    output = report.to_summary()
    with open(
        "data/fixtures/summary/multiline-scheme-error.txt", encoding="utf-8"
    ) as file:
        expected = file.read()
    assert output.count(expected.strip())
    assert output.count("File name (Not Found)")


def test_report_summary_valid():
    report = validate("data/capital-valid.csv")
    output = report.to_summary()
    assert (
        output.count("valid") and output.count("Summary") and not output.count("Errors")
    )


def test_report_summary_invalid():
    report = validate("data/countries.csv")
    output = report.to_summary()
    assert output.count("invalid") and output.count("Summary") and output.count("Errors")


def test_report_summary_validate_summary_valid():
    report = validate("data/capital-valid.csv")
    output = report.to_summary()
    file_size = 50 if IS_UNIX else 56
    assert (
        output.count("valid")
        and output.count("Summary")
        and output.count("File name              | data/capital-valid.csv")
        and output.count(f"File size (bytes)      | {file_size}                    ")
        and output.count("Total Time Taken (sec) | ")
    )


def test_report_summary_validate_summary_invalid():
    report = validate("data/capital-invalid.csv")
    output = report.to_summary()
    file_size = 171 if IS_UNIX else 183
    assert (
        output.count("invalid")
        and output.count("Summary")
        and output.count("File name                         | data/capital-invalid.csv")
        and output.count(f"File size (bytes)                 | {file_size}          ")
        and output.count("Total Time Taken (sec)            |")
        and output.count("Total Errors                      | 5          ")
        and output.count("Duplicate Label (duplicate-label) | 1          ")
        and output.count("Missing Cell (missing-cell)       | 1          ")
        and output.count("Blank Row (blank-row)             | 1          ")
        and output.count("Type Error (type-error)           | 1          ")
        and output.count("Extra Cell (extra-cell)           | 1          ")
    )


def test_report_summary_validate_multiline_errors():
    report = validate("data/countries.csv")
    output = report.to_summary()
    with open("data/fixtures/summary/multiline-errors.txt", encoding="utf-8") as file:
        expected = file.read()
    assert output.count(expected.strip())


def test_report_summary_partial_validation():
    report = validate("data/capital-invalid.csv", limit_errors=2)
    output = report.to_summary()
    assert (
        output.count("The document was partially validated because of one of the limits")
        and output.count("limit errors")
        and output.count("memory Limit")
        and output.count("Rows Checked(Partial)**           | 10")
    )
