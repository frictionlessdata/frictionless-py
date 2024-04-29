from typer.testing import CliRunner

from frictionless import __version__
from frictionless.console import console

runner = CliRunner()


# General


def test_console():
    result = runner.invoke(console)
    assert result.exit_code == 2
    assert result.stdout.count("Usage")


def test_console_version():
    result = runner.invoke(console, "--version")
    assert result.exit_code == 0
    assert result.stdout.count(__version__)


def test_console_help():
    result = runner.invoke(console, "--help")
    assert result.exit_code == 0
    assert result.stdout.count("Usage")


def test_console_error_bad_command():
    result = runner.invoke(console, "bad")
    assert result.exit_code == 2
    assert result.stdout.count("No such command 'bad'")
