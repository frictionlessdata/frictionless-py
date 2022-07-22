import json
import pytest
from typer.testing import CliRunner
from frictionless.program import program

runner = CliRunner()


def test_program_convert_yaml():
    result = runner.invoke(program, "convert data/datapackage.json --yaml")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/package.yaml"
    with open(output_file_path, encoding="utf-8") as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_markdown_with_path(tmpdir):

    # Write
    output_file_path = f"{tmpdir}/package.md"
    result = runner.invoke(
        program, f"convert data/datapackage.json --path {output_file_path} --markdown"
    )
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/package.md"
    with open(output_file_path, encoding="utf-8") as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_yaml_with_path(tmpdir):

    # Write
    output_file_path = f"{tmpdir}/package.yaml"
    result = runner.invoke(
        program, f"convert data/datapackage.json --path {output_file_path} --yaml"
    )
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/package.yaml"
    with open(output_file_path, encoding="utf-8") as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_er_diagram(tmpdir):

    # Write
    output_file_path = f"{tmpdir}/package.dot"
    result = runner.invoke(
        program, f"convert data/datapackage.json --path {output_file_path} --er-diagram"
    )
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/package.dot"
    with open(expected_file_path, encoding="utf-8") as file:
        expected = file.read()
    with open(output_file_path, encoding="utf-8") as file:
        assert expected.strip() == file.read().strip()


def test_program_convert_er_diagram_error(tmpdir):

    # Write
    output_file_path = f"{tmpdir}/package.dot"
    result = runner.invoke(
        program, f"convert data/schema.json --path {output_file_path} --er-diagram"
    )
    assert result.exit_code == 1
    assert result.stdout.count("ER-diagram format is only available for package")


def test_program_convert_yaml_without_source():
    result = runner.invoke(program, "convert")
    assert result.exit_code == 1
    assert result.stdout.count('Providing "source" is required')


def test_program_convert_yaml_without_target():
    result = runner.invoke(program, "convert data/datapackage.json ")
    assert result.exit_code == 1
    assert result.stdout.count("No format specified. For example --yaml")


def test_program_convert_with_wrong_source_file():
    result = runner.invoke(program, "convert data/datapackages.json --yaml")
    assert result.exit_code == 1
    assert result.stdout.count("File not found or not supported type of metadata")


def test_program_convert_resource_yaml():
    result = runner.invoke(program, "convert data/resource.json --yaml")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/resource.yaml"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_schema_yaml():
    result = runner.invoke(program, "convert data/schema.json --yaml")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/schema.yaml"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_checklist_yaml():
    result = runner.invoke(program, "convert data/checklist.json --yaml")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/checklist.yaml"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_dialect_yaml():
    result = runner.invoke(program, "convert data/dialect.json --yaml")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/dialect.yaml"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_report_yaml():
    result = runner.invoke(program, "convert data/report.json --yaml")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/report.yaml"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_inquiry_yaml():
    result = runner.invoke(program, "convert data/inquiry.json --yaml")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/inquiry.yaml"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_detector_yaml():
    result = runner.invoke(program, "convert data/detector.json --yaml")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/detector.yaml"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.xfail
def test_program_convert_pipeline_yaml():
    result = runner.invoke(program, "convert data/pipeline.json --yaml")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/pipeline.yaml"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_json():
    result = runner.invoke(program, "convert data/package.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "name": "test-tabulator",
        "resources": [
            {
                "name": "first-resource",
                "path": "table.xls",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "number"},
                        {"name": "name", "type": "string"},
                    ]
                },
            },
            {
                "name": "number-two",
                "path": "table-reverse.csv",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
            },
        ],
    }


def test_program_convert_resource_json():
    result = runner.invoke(program, "convert data/resource.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"name": "name", "path": "table.csv"}


def test_program_convert_schema_json():
    result = runner.invoke(program, "convert data/schema.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }


def test_program_convert_checklist_json():
    result = runner.invoke(program, "convert data/checklist.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "checks": [
            {
                "type": "deviated-cell",
                "interval": 3,
                "ignoreFields": ["Latitudine", "Longitudine"],
            }
        ]
    }


def test_program_convert_dialect_json():
    result = runner.invoke(program, "convert data/dialect.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"csv": {"delimiter": ";"}}


def test_program_convert_report_json():
    result = runner.invoke(program, "convert data/report.yaml --json")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/report.json"
    with open(output_file_path) as file:
        assert json.loads(result.stdout) == json.loads(file.read())


def test_program_convert_inquiry_json():
    result = runner.invoke(program, "convert data/inquiry.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "tasks": [
            {"path": "data/capital-valid.csv"},
            {"path": "data/capital-invalid.csv"},
        ]
    }


def test_program_convert_detector_json():
    result = runner.invoke(program, "convert data/detector.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "fieldConfidence": 1,
        "fieldFloatNumbers": True,
        "fieldMissingValues": ["", "67"],
    }


def test_program_convert_pipeline_json():
    result = runner.invoke(program, "convert data/pipeline.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "name": "pipeline",
        "steps": [{"type": "cell-set", "fieldName": "population", "value": 100}],
    }


def test_program_convert_package_markdown():
    result = runner.invoke(program, "convert data/datapackage.json --markdown")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/package.md"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_resource_markdown():
    result = runner.invoke(program, "convert data/resource.json --markdown")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/resource.md"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_schema_markdown():
    result = runner.invoke(program, "convert data/schema.json --markdown")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/schema.md"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_checklist_markdown():
    result = runner.invoke(program, "convert data/checklist.json --markdown")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/checklist.md"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_dialect_markdown():
    result = runner.invoke(program, "convert data/dialect.json --markdown")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/dialect.md"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.xfail
def test_program_convert_report_markdown():
    result = runner.invoke(program, "convert data/report.json --markdown")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/report.md"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_inquiry_markdown():
    result = runner.invoke(program, "convert data/inquiry.json --markdown")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/inquiry.md"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


def test_program_convert_detector_markdown():
    result = runner.invoke(program, "convert data/detector.json --markdown")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/detector.md"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.xfail
def test_program_convert_pipeline_markdown():
    result = runner.invoke(program, "convert data/pipeline.json --markdown")
    assert result.exit_code == 0

    # Read
    output_file_path = "data/fixtures/convert/pipeline.md"
    with open(output_file_path) as file:
        assert result.stdout.count(file.read().strip())
