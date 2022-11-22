import json
from frictionless import Resource, Report


# General


def test_report_to_summary_error_not_found():
    resource = Resource("data/countriess.csv")
    report = resource.validate()
    output = report.to_summary()

    # Read
    expected_file_path = "data/fixtures/summary/multiline-scheme-error.txt"
    with open(expected_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert output.count(expected.strip())
    assert output.count("(file not found)")


def test_report_to_summary_valid():
    resource = Resource("data/capital-valid.csv")
    report = resource.validate()
    output = report.to_summary()
    assert output.count("valid")
    assert output.count("Summary")
    assert not output.count("Errors")


def test_report_to_summary_invalid():
    resource = Resource("data/countriess.csv")
    report = resource.validate()
    output = report.to_summary()
    assert output.count("invalid")
    assert output.count("Summary")
    assert output.count("Errors")


def test_report_to_summary_validate_multiline_errors():
    resource = Resource("data/countries.csv")
    report = resource.validate()
    output = report.to_summary()
    path = "data/fixtures/summary/multiline-errors.txt"
    with open(path, encoding="utf-8") as file:
        expected = file.read()
    print(output)
    assert output.count(expected.strip())


# Bugs


def test_report_to_json_with_bytes_serialization_issue_836():
    source = b"header1,header2\nvalue1,value2\nvalue3,value4"
    resource = Resource(source)
    report = resource.validate()
    print(report.to_descriptor())
    descriptor = report.to_json()
    assert descriptor


def test_report_to_yaml_with_bytes_serialization_issue_836():
    source = b"header1,header2\nvalue1,value2\nvalue3,value4"
    resource = Resource(source)
    report = resource.validate()
    descriptor = report.to_yaml()
    assert "binary" not in descriptor


# Yaml


def test_report_to_yaml():
    report = Report.from_descriptor("data/report.json")
    output_file_path = "data/report.yaml"
    with open(output_file_path) as file:
        assert report.to_yaml().strip() == file.read().strip()


# Json


def test_report_to_json():
    report = Report.from_descriptor("data/report.yaml")

    # Read
    output_file_path = "data/report.json"
    with open(output_file_path) as file:
        assert json.loads(report.to_json()) == json.loads(file.read())
