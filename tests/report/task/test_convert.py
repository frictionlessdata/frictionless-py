from frictionless import Resource, platform


# General


def test_report_task_to_summary_valid():
    resource = Resource("data/capital-valid.csv")
    report = resource.validate()
    output = report.tasks[0].to_summary()
    assert output.count("File Place   | data/capital-valid.csv")
    assert output.count("Total Time   |")
    if platform.type != "windows":
        assert output.count("File Size    | 50 Bytes")


def test_report_task_to_summary_invalid():
    resource = Resource("data/capital-invalid.csv")
    report = resource.validate()
    output = report.tasks[0].to_summary()
    assert output.count("File Place      | data/capital-invalid.csv")
    assert output.count("Total Time      |")
    assert output.count("Total Errors    | 5")
    assert output.count("Duplicate Label | 1")
    assert output.count("Missing Cell    | 1")
    assert output.count("Blank Row       | 1")
    assert output.count("Type Error      | 1")
    assert output.count("Extra Cell      | 1")
    if platform.type != "windows":
        assert output.count("File Size       | 171 Bytes")


def test_report_task_to_summary_file_not_found():
    resource = Resource("bad.csv")
    report = resource.validate()
    output = report.tasks[0].to_summary()
    assert output.count("File Place   | bad.csv")
    assert output.count("File Size    | (file not found)")
    assert output.count("Total Time   |")
    assert output.count("Total Errors | 1")
    assert output.count("Scheme Error | 1")


def test_report_reporttask_summary_zippedfile():
    resource = Resource("data/table.csv.zip")
    report = resource.validate()
    output = report.tasks[0].to_summary()
    print(output)
    assert output.count("data/table.csv.zip -> table.csv") and output.count("198")


def test_report_task_to_summary_last_row_checked():
    resource = Resource("data/capital-invalid.csv")
    report = resource.validate(limit_errors=2)
    output = report.tasks[0].to_summary()
    assert output.count("> reached error limit: 2")
    assert output.count("Rows Checked    | 9")
    assert output.count("Total Errors    | 2")
    assert output.count("Duplicate Label | 1")
    assert output.count("Missing Cell    | 1")


def test_report_task_to_summary_errors_with_count():
    resource = Resource("data/capital-invalid.csv")
    report = resource.validate()
    output = report.tasks[0].to_summary()
    assert output.count("Total Errors    | 5")
    assert output.count("Duplicate Label | 1")
    assert output.count("Missing Cell    | 1")
    assert output.count("Blank Row       | 1")
    assert output.count("Type Error      | 1")
    assert output.count("Extra Cell      | 1")
