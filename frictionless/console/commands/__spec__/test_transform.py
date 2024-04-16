from typer.testing import CliRunner

from frictionless.console import console

runner = CliRunner()


def test_console_transform():
    result = runner.invoke(
        console,
        "transform data/transform.csv --pipeline data/pipeline.yaml",
    )
    assert result.exit_code == 0
    assert result.stdout.count("id")
    assert result.stdout.count("name")
    assert result.stdout.count("population")


def test_console_transform_error_not_found():
    result = runner.invoke(
        console,
        "transform data/transform.csv --pipeline data/bad.yaml",
    )
    assert result.exit_code == 1
    #  assert result.stdout.count("[Errno 2]")
    #  assert result.stdout.count("data/bad.yaml")


# Bugs


def test_console_transform_error_not_found_source_issue_814():
    result = runner.invoke(
        console,
        "transform data/bad.csv --pipeline data/issue-814.yaml",
    )
    assert result.exit_code == 1
    assert result.stdout.count("[Errno 2]")
    assert result.stdout.count("bad.csv")
