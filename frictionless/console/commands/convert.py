from __future__ import annotations

from typing import List

import typer
from rich.console import Console
from rich.progress import track

from ...exception import FrictionlessException
from ...platform import platform
from ...resource import Resource
from ...system import system
from .. import common, helpers
from ..console import console


@console.command(name="convert")
def console_convert(
    # Resource
    source: List[str] = common.source,
    name: str = common.resource_name,
    type: str = common.type,
    path: str = common.path,
    scheme: str = common.scheme,
    format: str = common.format,
    compression: str = common.compression,
    innerpath: str = common.innerpath,
    encoding: str = common.encoding,
    schema: str = common.schema,
    basepath: str = common.basepath,
    # Dialect
    dialect: str = common.dialect,
    header_rows: str = common.header_rows,
    header_join: str = common.header_join,
    comment_char: str = common.comment_char,
    comment_rows: str = common.skip_rows,
    sheet: str = common.sheet,
    table: str = common.table,
    keys: str = common.keys,
    keyed: bool = common.keyed,
    # Command
    to_path: str = common.path,
    to_format: str = common.format,
    to_dialect: str = common.dialect,
    to_csv_delimiter: str = typer.Option(default=None),
    # System
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """
    Convert data table
    """
    console = Console()

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Create source
    source = helpers.create_source(source, path=path)
    if not source and not path:
        note = 'Providing "source" or "path" is required'
        helpers.print_error(console, note=note)
        raise typer.Exit(code=1)

    try:
        # Create dialect
        dialect_obj = helpers.create_dialect(
            descriptor=dialect,
            header_rows=header_rows,
            header_join=header_join,
            comment_char=comment_char,
            comment_rows=comment_rows,
            sheet=sheet,
            table=table,
            keys=keys,
            keyed=keyed,
        )

        # Create resource
        resource = Resource(
            source=helpers.create_source(source),
            path=path,
            scheme=scheme,
            format=format,
            datatype=type,
            compression=compression,
            innerpath=innerpath,
            encoding=encoding,
            schema=schema,
            basepath=basepath,
        )

        # Add dialect
        if dialect_obj:
            resource.dialect = dialect_obj

        # Create to_dialect
        to_dialect_obj = helpers.create_dialect(
            descriptor=to_dialect,
            csv_delimiter=to_csv_delimiter,
        )

        # Get resource
        # TODO: rework; don't use resources[0]
        resources = resource.list(name=name)
        resource = resources[0]

        # Ensure type
        if not isinstance(resource, platform.frictionless_resources.Convertible):
            note = f'Resource with data type "{resource.datatype}" is not convertible'
            raise FrictionlessException(note)

        # Convert resource
        console.rule("[bold]Convert")
        # TODO: replace dummy progress bar a normal one
        for stage in track(["start", "end"], description="Converting..."):
            if stage == "end":
                resource.convert(
                    to_path=to_path, to_format=to_format, to_dialect=to_dialect_obj
                )

    except Exception as exception:
        helpers.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Print result
    console.rule("[bold]Result")
    console.print(f"Succesefully converted to [bold]{to_path}[/bold]")
