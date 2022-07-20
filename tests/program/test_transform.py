import pytest
from typer.testing import CliRunner
from frictionless import platform
from frictionless.program import program

runner = CliRunner()


@pytest.mark.xfail(reason="Rework for the new Pipeline")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_program_transform():
    result = runner.invoke(program, "transform data/pipeline.yaml")
    assert result.exit_code == 0
    assert result.stdout.count("success: data/pipeline.yaml")


def test_program_transform_error_not_found():
    result = runner.invoke(program, "transform data/bad.yaml")
    assert result.exit_code == 1
    assert result.stdout.count("[Errno 2]") and result.stdout.count("data/bad.yaml")


@pytest.mark.xfail(reason="Rework for the new Pipeline")
def test_program_transform_error_not_found_source_issue_814():
    result = runner.invoke(program, "transform data/issue-814.yaml")
    assert result.exit_code == 1
    assert result.stdout.count("[Errno 2]") and result.stdout.count("bad.csv")
