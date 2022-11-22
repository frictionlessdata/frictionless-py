import pytest
from frictionless import (
    Detector,
    Dialect,
    Package,
    Pipeline,
    Checklist,
    Inquiry,
    Schema,
    Report,
    Resource,
)


SCHEMA = {
    "fields": [
        {
            "name": "id",
            "description": "Any positive integer",
            "type": "integer",
            "constraints": {"minimum": 1},
        },
        {
            "name": "age",
            "title": "Age",
            "description": "Any number >= 1",
            "type": "number",
            "constraints": {"minimum": 1},
        },
    ]
}
RESOURCE = {
    "name": "main",
    "path": "data/primary-file-types.csv",
    "schema": {
        "fields": [
            {
                "name": "id",
                "description": "Any positive integer",
                "type": "integer",
                "constraints": {"minimum": 1},
            },
            {
                "name": "integer_minmax",
                "description": "An integer between 1 and 10",
                "type": "integer",
                "constraints": {"minimum": 1, "maximum": 10},
            },
            {
                "name": "boolean",
                "description": "Any boolean",
                "type": "boolean",
            },
        ],
        "primaryKey": ["id"],
    },
}
PACKAGE = {
    "name": "package",
    "resources": [
        {
            "name": "main",
            "path": "data/primary-file-types.csv",
            "schema": {
                "fields": [
                    {
                        "name": "id",
                        "description": "Any positive integer",
                        "type": "integer",
                        "constraints": {"minimum": 1},
                    },
                    {
                        "name": "integer_minmax",
                        "description": "An integer between 1 and 10",
                        "type": "integer",
                        "constraints": {"minimum": 1, "maximum": 10},
                    },
                    {
                        "name": "boolean",
                        "description": "Any boolean",
                        "type": "boolean",
                    },
                ],
                "primaryKey": ["id"],
            },
        }
    ],
}


# Checklist


def test_checklist_markdown():
    checklist = Checklist.from_descriptor("data/checklist.json")
    output_file_path = "data/fixtures/convert/checklist.md"
    with open(output_file_path) as file:
        assert checklist.to_markdown().strip() == file.read()


# Detector


def test_detector_to_markdown():
    detector = Detector.from_descriptor("data/detector.json")
    output_file_path = "data/fixtures/convert/detector.md"
    with open(output_file_path) as file:
        assert detector.to_markdown().strip() == file.read()


# Dialect


def test_markdown_mapper_dialect_to_markdown():
    dialect = Dialect.from_descriptor("data/dialect.json")
    output_file_path = "data/fixtures/convert/dialect.md"
    with open(output_file_path) as file:
        assert dialect.to_markdown().strip() == file.read()


# Inquiry


def test_inquiry_to_markdown():
    inquiry = Inquiry.from_descriptor("data/inquiry.json")
    expected_file_path = "data/fixtures/convert/inquiry.md"

    # Read
    with open(expected_file_path) as file:
        assert inquiry.to_markdown().strip() == file.read()


# Package


def test_package_to_markdown():
    package = Package(PACKAGE)
    expected_file_path = "data/fixtures/output-markdown/package.md"

    # Reads
    with open(expected_file_path, encoding="utf-8") as file:
        print("\n", package.to_markdown().strip())
        assert package.to_markdown().strip() == file.read()


def test_package_to_markdown_file(tmpdir):
    package = Package(PACKAGE)
    output_file_path = str(tmpdir.join("package.md"))
    expected_file_path = "data/fixtures/output-markdown/package.md"

    # Read - expected
    with open(expected_file_path, encoding="utf-8") as file:
        expected = file.read()

    # Write
    package.to_markdown(path=output_file_path).strip()

    # Read - output
    with open(output_file_path, encoding="utf-8") as file:
        assert expected == file.read()


def test_package_to_markdown_table():
    package = Package(PACKAGE)
    expected_file_path = "data/fixtures/output-markdown/package-table.md"

    # Read
    with open(expected_file_path, encoding="utf-8") as file:
        assert package.to_markdown(table=True).strip() == file.read()


# Pipeline


def test_pipeline_to_markdown():
    pipeline = Pipeline.from_descriptor("data/pipeline.json")
    expected_file_path = "data/fixtures/convert/pipeline.md"

    # Read
    with open(expected_file_path) as file:
        assert pipeline.to_markdown().strip() == file.read()


# Report


@pytest.mark.skip
def test_report_to_markdown():
    report = Report.from_descriptor("data/report.json")
    output_file_path = "data/fixtures/convert/report.md"
    with open(output_file_path) as file:
        assert report.to_markdown().strip() == file.read()


# Resource


def test_resource_to_markdown_path_schema():
    resource = Resource(RESOURCE)
    expected_file_path = "data/fixtures/output-markdown/resource.md"

    # Read
    with open(expected_file_path, encoding="utf-8") as file:
        assert resource.to_markdown().strip() == file.read()


def test_resource_to_markdown_path_schema_table():
    resource = Resource(RESOURCE)
    expected_file_path = "data/fixtures/output-markdown/resource-table.md"

    # Read
    with open(expected_file_path, encoding="utf-8") as file:
        print("")
        print(resource.to_markdown(table=True).strip())
        assert resource.to_markdown(table=True).strip() == file.read().strip()


def test_resource_to_markdown_file(tmpdir):
    resource = Resource(RESOURCE)
    expected_file_path = "data/fixtures/output-markdown/resource.md"
    target = str(tmpdir.join("resource.md"))
    resource.to_markdown(path=target).strip()

    # Read - expected
    with open(expected_file_path, encoding="utf-8") as file:
        expected = file.read()

    # Read - output
    with open(target, encoding="utf-8") as file:
        assert expected == file.read()


# Schema


def test_schema_to_markdown():
    schema = Schema.from_descriptor(SCHEMA)
    md_file_path = "data/fixtures/output-markdown/schema.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert schema.to_markdown().strip() == expected


def test_schema_to_markdown_table():
    schema = Schema.from_descriptor(SCHEMA)

    # Read
    expected_file_path = "data/fixtures/output-markdown/schema-table.md"
    with open(expected_file_path, encoding="utf-8") as file:
        assert schema.to_markdown(table=True).strip() == file.read().strip()


def test_schema_to_markdown_file(tmpdir):
    schema = Schema.from_descriptor(SCHEMA)

    # Read - expected
    expected_file_path = "data/fixtures/output-markdown/schema.md"
    with open(expected_file_path, encoding="utf-8") as file:
        expected = file.read()

    # Write
    output_file_path = str(tmpdir.join("schema.md"))
    schema.to_markdown(path=output_file_path).strip()

    # Read - output
    with open(output_file_path, encoding="utf-8") as file:
        assert expected == file.read()
