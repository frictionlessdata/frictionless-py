from __future__ import annotations

from typer.testing import CliRunner


def create_runner() -> CliRunner:
    """Build a runner capturing stdout and stderr separately.

    click >= 8.2 always separates the two streams and dropped the "mix_stderr"
    argument, while earlier versions merge them unless it is passed. Python 3.9
    is stuck on click 8.1 because 8.2 requires Python 3.10.
    """
    try:
        return CliRunner(mix_stderr=False)  # type: ignore[call-arg]
    except TypeError:
        return CliRunner()
