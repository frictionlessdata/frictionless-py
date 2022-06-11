import pytest
from typer.testing import CliRunner
from frictionless import program, helpers

runner = CliRunner()


# General
# TODO: rework on the new pipeline usage


@pytest.mark.skip
@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_program_transform():
    result = runner.invoke(program, "transform data/pipeline.yaml")
    assert result.exit_code == 0
    assert result.stdout.count("success: data/pipeline.yaml")


@pytest.mark.skip
def test_program_transform_error_not_found():
    result = runner.invoke(program, "transform data/bad.yaml")
    assert result.exit_code == 1
    assert result.stdout.count("[Errno 2]") and result.stdout.count("data/bad.yaml")


@pytest.mark.skip
def test_program_transform_error_not_found_source_issue_814():
    result = runner.invoke(program, "transform data/issue-814.yaml")
    assert result.exit_code == 1
    assert result.stdout.count("[Errno 2]") and result.stdout.count("bad.csv")
