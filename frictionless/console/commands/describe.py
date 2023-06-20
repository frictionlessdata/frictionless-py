from __future__ import annotations

from typing import List

import typer
from rich.console import Console
from rich.table import Table

from ...dialect import Dialect
from ...package import Package
from ...resource import Resource
from ...resources import TableResource
from ...schema import Schema
from ...system import system
from .. import common, helpers
from ..console import console

DEFAULT_MAX_FIELDS = 10


@console.command(name="describe")
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
    # TODO: allow cherry-picking stats for adding to a descriptor
    stats: bool = common.stats,
    yaml: bool = common.yaml,
    json: bool = common.json,
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """
    Describe a data source.

    Based on the inferred data source type it will return resource or package descriptor.
    Default output format is YAML with a front matter.
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

        # Describe source
        metadata = Resource.describe(
            source=helpers.create_source(source),
            name=name,
            type=type,
            path=path,
            scheme=scheme,
            format=format,
            compression=compression,
            innerpath=innerpath,
            encoding=encoding,
            dialect=dialect_obj,
            basepath=basepath,
            detector=detector_obj,
            stats=stats,
        )
    except Exception as exception:
        helpers.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Json mode
    if json:
        descriptor = metadata.to_json()
        print(descriptor)
        raise typer.Exit()

    # Yaml mode
    if yaml or isinstance(metadata, (Dialect, Schema)):
        descriptor = metadata.to_yaml().strip()
        print(descriptor)
        raise typer.Exit()

    # Default mode
    console.rule("[bold]Dataset")
    assert isinstance(metadata, (Resource, Package))
    resources = [metadata] if isinstance(metadata, Resource) else metadata.resources
    view = Table(title="dataset")
    view.add_column("name")
    view.add_column("type")
    view.add_column("path")
    if stats:
        view.add_column("hash")
        view.add_column("bytes")
        view.add_column("fields")
        view.add_column("rows")
    for resource in resources:
        style = "sky_blue1" if resource.tabular else ""
        row = [resource.name, resource.type, resource.path]
        if stats:
            row.append(str(resource.hash))
            row.append(str(resource.bytes))
            row.append(str(resource.fields or ""))
            row.append(str(resource.rows or ""))
        view.add_row(*row, style=style)
    console.print(view)
    console.rule("[bold]Tables")
    for resource in resources:
        if isinstance(resource, TableResource):
            view = Table(title=resource.name)
            labels = list(resource.schema.field_names)
            for label in labels[:DEFAULT_MAX_FIELDS]:
                view.add_column(label)
            if len(labels) > DEFAULT_MAX_FIELDS:
                view.add_column("...")
            row = resource.schema.field_types[:DEFAULT_MAX_FIELDS]
            if len(labels) > DEFAULT_MAX_FIELDS:
                row.append("...")
            view.add_row(*row)
            console.print(view)
