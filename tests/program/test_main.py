from typer.testing import CliRunner
from frictionless import program, __version__

runner = CliRunner()


# General


def test_describe():
    result = runner.invoke(program)
    assert result.exit_code == 0
    assert result.stdout.count("Usage")


def test_describe_version():
    result = runner.invoke(program, "--version")
    assert result.exit_code == 0
    assert result.stdout.count(__version__)


def test_describe_help():
    result = runner.invoke(program, "--help")
    assert result.exit_code == 0
    assert result.stdout.count("Usage")


def test_describe_error_bad_command():
    result = runner.invoke(program, "bad")
    assert result.exit_code == 2
    assert result.stdout.count("No such command 'bad'")
