from typer.testing import CliRunner
from frictionless import program, helpers

runner = CliRunner()
IS_UNIX = not helpers.is_platform("windows")


# General


def test_program_transform():
    result = runner.invoke(program, "transform data/pipeline.yaml")
    assert result.exit_code == 0
    if IS_UNIX:
        assert result.stdout.count("success: data/pipeline.yaml")


def test_program_transform_error_not_found():
    result = runner.invoke(program, "transform data/bad.yaml")
    assert result.exit_code == 1
    assert result.stdout.count("No such file or directory: 'data/bad.yaml'")
