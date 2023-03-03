from __future__ import annotations
import typer
from .program import program
from . import common


@program.command(name="explore")
def program_explore(
    source: str = typer.Argument(default=None),
    # Options
    debug: bool = common.debug,
):
    """Query data"""
    pass
