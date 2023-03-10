from __future__ import annotations
import re
import os
import atexit
import typer
import tempfile
from typing import List
from rich.console import Console
from ..resource import Resource
from .program import program
from ..system import system
from .. import helpers
from . import common
from . import utils


@program.command(name="script")
def program_script(
    # Resource
    source: List[str] = common.source,
    name: str = common.resource_name,
    type: str = common.type,
    path: str = common.path,
    # System
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """Script data"""
    console = Console()

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Create source
    source = utils.create_source(source, path=path)
    if not source and not path:
        note = 'Providing "source" or "path" is required'
        utils.print_error(console, note=note)
        raise typer.Exit(code=1)

    # Index resource
    console.rule("[bold]Index")
    try:
        # Create resource
        resource = Resource(
            source=utils.create_source(source),
            name=name,
            path=path,
            datatype=type or "",
        )

        # Create database
        file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        atexit.register(os.remove, file.name)
        database = file.name

        # Index resources
        names = []
        resources = resource.list(name=name)
        for resource in resources:
            names.extend(
                utils.index_resource(
                    console,
                    resource=resource,
                    database=database,
                    fast=True,
                    use_fallback=True,
                    debug=debug,
                )
            )
    except Exception as exception:
        utils.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Ensure tables
    if not names:
        note = "Not found any tabular resources"
        utils.print_error(console, note=note)
        raise typer.Exit(1)

    # Enter interpreter
    console.rule("[bold]Script")
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    atexit.register(os.remove, file.name)
    startup = generate_startup(database, names=names)
    helpers.write_file(file.name, startup)
    os.system(f"PYTHONSTARTUP={file.name} python3")


# Internal


def generate_startup(database: str, *, names: List[str]) -> str:
    if "://" not in database:
        database = f"sqlite:///{database}"
    lines: List[str] = []
    lines.append("import sqlalchemy as sa")
    lines.append("import pandas as pd")
    lines.append(f"engine = sa.create_engine('{database}')")
    lines.append("conn = engine.connect()")
    dfnames = []
    for name in names:
        dfname = generate_dfname(name)
        dfnames.append(dfname)
        lines.append(f"{dfname} = pd.read_sql('{name}', conn)")
    lines.append(f"print('Available data frames: {', '.join(dfnames)}')")
    return "\n".join(lines)


def generate_dfname(name: str) -> str:
    return "df_" + re.sub("[^0-9a-zA-Z_]+", "_", name)
