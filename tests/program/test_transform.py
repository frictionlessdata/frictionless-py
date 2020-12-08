import pytest
from typer.testing import CliRunner
from frictionless import program, helpers

runner = CliRunner()


# General


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_transform():
    result = runner.invoke(program, "transform data/pipeline.yaml")
    assert result.exit_code == 0
    assert result.stdout.count('success: "data/pipeline.yaml"')


def test_transform_error_not_found():
    result = runner.invoke(program, "transform data/bad.yaml")
    assert result.exit_code == 1
    assert result.stdout.count("No such file or directory: 'data/bad.yaml'")
