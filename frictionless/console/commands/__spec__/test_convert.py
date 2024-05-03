import json

import pytest
import yaml
from typer.testing import CliRunner

from frictionless import platform
from frictionless.console import console

runner = CliRunner()


@pytest.mark.skip
def test_console_convert_yaml():
    result = runner.invoke(console, "convert data/datapackage.json --yaml")
    expected_file_path = "data/package.yaml"

    # Read
    with open(expected_file_path) as file:
        assert yaml.safe_load(result.stdout) == yaml.safe_load(file.read())
    assert result.exit_code == 0


@pytest.mark.skip
def test_console_convert_markdown_with_path(tmpdir):
    # Write
    output_file_path = f"{tmpdir}/package.md"
    result = runner.invoke(
        console, f"convert data/datapackage.json --path {output_file_path} --markdown"
    )
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/package.md"
    with open(expected_file_path, encoding="utf-8") as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_yaml_with_path(tmpdir):
    # Write
    output_file_path = f"{tmpdir}/package.yaml"
    result = runner.invoke(
        console, f"convert data/datapackage.json --path {output_file_path} --yaml"
    )
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/package.yaml"
    with open(expected_file_path, encoding="utf-8") as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_console_convert_er_diagram(tmpdir):
    # Write
    output_file_path = f"{tmpdir}/package.dot"
    result = runner.invoke(
        console, f"convert data/datapackage.json --path {output_file_path} --er-diagram"
    )
    assert result.exit_code == 0

    # Read - expected
    expected_file_path = "data/fixtures/convert/package.dot"
    with open(expected_file_path, encoding="utf-8") as file:
        expected = file.read()

    # Read - output
    with open(output_file_path, encoding="utf-8") as file:
        assert expected.strip() == file.read().strip()


@pytest.mark.skip
def test_console_convert_er_diagram_error(tmpdir):
    # Write
    output_file_path = f"{tmpdir}/package.dot"
    result = runner.invoke(
        console, f"convert data/schema.json --path {output_file_path} --er-diagram"
    )
    assert result.exit_code == 1
    assert result.stdout.count("ER-diagram format is only available for package")


@pytest.mark.skip
def test_console_convert_yaml_without_source():
    result = runner.invoke(console, "convert")
    assert result.exit_code == 1
    assert result.stdout.count('Providing "source" is required')


@pytest.mark.skip
def test_console_convert_yaml_without_target():
    result = runner.invoke(console, "convert data/datapackage.json ")
    assert result.exit_code == 1
    assert result.stdout.count("No format specified. For example --yaml")


@pytest.mark.skip
def test_console_convert_with_wrong_source_file():
    result = runner.invoke(console, "convert data/datapackages.json --yaml")
    assert result.exit_code == 1
    assert result.stdout.count("File not found or not supported type of metadata")


@pytest.mark.skip
def test_console_convert_resource_yaml():
    result = runner.invoke(console, "convert data/resource.json --yaml")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/resource.yaml"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_schema_yaml():
    result = runner.invoke(console, "convert data/schema.json --yaml")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/schema.yaml"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_checklist_yaml():
    result = runner.invoke(console, "convert data/checklist.json --yaml")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/checklist.yaml"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_dialect_yaml():
    result = runner.invoke(console, "convert data/dialect.json --yaml")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/dialect.yaml"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_report_yaml():
    result = runner.invoke(console, "convert data/report.json --yaml")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/report.yaml"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_inquiry_yaml():
    result = runner.invoke(console, "convert data/inquiry.json --yaml")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/inquiry.yaml"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_pipeline_yaml():
    result = runner.invoke(console, "convert data/pipeline.json --yaml")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/pipeline.yaml"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_json():
    result = runner.invoke(console, "convert data/package.yaml --json")
    expected_file_path = "data/datapackage.json"

    # Read
    with open(expected_file_path) as file:
        assert json.loads(result.stdout) == json.loads(file.read())


@pytest.mark.skip
def test_console_convert_resource_json():
    result = runner.invoke(console, "convert data/resource.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"name": "name", "path": "table.csv"}


@pytest.mark.skip
def test_console_convert_schema_json():
    result = runner.invoke(console, "convert data/schema.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }


@pytest.mark.skip
def test_console_convert_checklist_json():
    result = runner.invoke(console, "convert data/checklist.yaml --json")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/checklist.json"
    with open(expected_file_path) as file:
        assert json.loads(result.stdout) == json.loads(file.read())


@pytest.mark.skip
def test_console_convert_dialect_json():
    result = runner.invoke(console, "convert data/dialect.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"csv": {"delimiter": ";"}}


@pytest.mark.skip
def test_console_convert_report_json():
    result = runner.invoke(console, "convert data/report.yaml --json")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/report.json"
    with open(expected_file_path) as file:
        assert json.loads(result.stdout) == json.loads(file.read())


@pytest.mark.skip
def test_console_convert_inquiry_json():
    result = runner.invoke(console, "convert data/inquiry.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "tasks": [
            {"path": "data/capital-valid.csv"},
            {"path": "data/capital-invalid.csv"},
        ]
    }


@pytest.mark.skip
def test_console_convert_pipeline_json():
    result = runner.invoke(console, "convert data/pipeline.yaml --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "name": "pipeline",
        "steps": [{"type": "cell-set", "fieldName": "population", "value": 100}],
    }


@pytest.mark.skip
def test_console_convert_package_markdown():
    result = runner.invoke(console, "convert data/datapackage.json --markdown")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/package.md"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_resource_markdown():
    result = runner.invoke(console, "convert data/resource.json --markdown")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/resource.md"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_schema_markdown():
    result = runner.invoke(console, "convert data/schema.json --markdown")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/schema.md"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_checklist_markdown():
    result = runner.invoke(console, "convert data/checklist.json --markdown")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/checklist.md"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_dialect_markdown():
    result = runner.invoke(console, "convert data/dialect.json --markdown")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/dialect.md"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_report_markdown():
    result = runner.invoke(console, "convert data/report.json --markdown")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/report.md"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_inquiry_markdown():
    result = runner.invoke(console, "convert data/inquiry.json --markdown")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/inquiry.md"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())


@pytest.mark.skip
def test_console_convert_pipeline_markdown():
    result = runner.invoke(console, "convert data/pipeline.json --markdown")
    assert result.exit_code == 0

    # Read
    expected_file_path = "data/fixtures/convert/pipeline.md"
    with open(expected_file_path) as file:
        assert result.stdout.count(file.read().strip())
