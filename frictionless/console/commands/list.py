from __future__ import annotations

from typing import List

import typer
from rich.console import Console
from rich.table import Table

from ...helpers import to_json, to_yaml
from ...resource import Resource
from ...system import system
from .. import common, helpers
from ..console import console


@console.command(name="list")
def console_describe(
    # Source
    source: List[str] = common.source,
    name: str = common.resource_name,
    type: str = common.type,
    path: str = common.path,
    scheme: str = common.scheme,
    format: str = common.format,
    encoding: str = common.encoding,
    innerpath: str = common.innerpath,
    compression: str = common.compression,
    # Dialect
    dialect: str = common.dialect,
    header_rows: str = common.header_rows,
    header_join: str = common.header_join,
    comment_char: str = common.comment_char,
    comment_rows: str = common.comment_rows,
    sheet: str = common.sheet,
    table: str = common.table,
    keys: str = common.keys,
    keyed: bool = common.keyed,
    # Detector
    buffer_size: int = common.buffer_size,
    sample_size: int = common.sample_size,
    field_type: str = common.field_type,
    field_names: str = common.field_names,
    field_confidence: float = common.field_confidence,
    field_float_numbers: bool = common.field_float_numbers,
    field_missing_values: str = common.field_missing_values,
    # Command
    basepath: str = common.basepath,
    yaml: bool = common.yaml,
    json: bool = common.json,
    # System
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """
    List a data source.
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

        # Create detector
        detector_obj = helpers.create_detector(
            buffer_size=buffer_size,
            sample_size=sample_size,
            field_type=field_type,
            field_names=field_names,
            field_confidence=field_confidence,
            field_float_numbers=field_float_numbers,
            field_missing_values=field_missing_values,
        )

        # Create resource
        resource = Resource(
            source=helpers.create_source(source),
            name=name,
            path=path,
            scheme=scheme,
            format=format,
            datatype=type,
            compression=compression,
            innerpath=innerpath,
            encoding=encoding,
            basepath=basepath,
            detector=detector_obj,
        )

        # Add dialect
        if dialect_obj:
            resource.dialect = dialect_obj

        # List resources
        resources = resource.list(name=name)
        descriptors = [resource.to_descriptor() for resource in resources]
    except Exception as exception:
        helpers.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Yaml mode
    if yaml:
        descriptor = to_yaml(descriptors).strip()
        print(descriptor)
        raise typer.Exit()

    # Json mode
    if json:
        descriptor = to_json(descriptors).strip()
        print(descriptor)
        raise typer.Exit()

    # Default mode
    console.rule("[bold]Dataset")
    view = Table(title="dataset")
    view.add_column("name")
    view.add_column("type")
    view.add_column("path")
    for resource in resources:
        style = "sky_blue1" if resource.tabular else ""
        row = [resource.name, resource.type, resource.path]
        view.add_row(*row, style=style)
    console.print(view)
