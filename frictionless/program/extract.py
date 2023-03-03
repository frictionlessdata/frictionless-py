from __future__ import annotations
import sys
import typer
import json as pyjson
from rich.table import Table
from rich.console import Console
from typing import TYPE_CHECKING, List, Optional
from ..resource import Resource
from ..platform import platform
from ..system import system
from .program import program
from .. import helpers
from . import factory
from . import common

if TYPE_CHECKING:
    from ..interfaces import IFilterFunction, IProcessFunction


@program.command(name="extract")
def program_extract(
    # Resource
    source: List[str] = common.source,
    type: str = common.type,
    path: str = common.path,
    scheme: str = common.scheme,
    format: str = common.format,
    compression: str = common.compression,
    innerpath: str = common.innerpath,
    encoding: str = common.encoding,
    basepath: str = common.basepath,
    schema: str = common.schema,
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
    # Detector
    buffer_size: int = common.buffer_size,
    sample_size: int = common.sample_size,
    field_type: str = common.field_type,
    field_names: str = common.field_names,
    field_confidence: float = common.field_confidence,
    field_float_numbers: bool = common.field_float_numbers,
    field_missing_values: str = common.field_missing_values,
    schema_sync: bool = common.schema_sync,
    # Command
    name: str = common.resource_name,
    valid: bool = common.valid_rows,
    invalid: bool = common.invalid_rows,
    limit_rows: int = common.limit_rows,
    yaml: bool = common.yaml,
    json: bool = common.json,
    csv: bool = common.csv,
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
    # TODO: review
    keep_delimiter: bool = common.keep_delimiter,
    # TODO: deprecate
    resource_name: str = common.resource_name,
):
    """
    Extract rows from a data source.

    Based on the inferred data source type it will return resource or package data.
    Default output format is tabulated with a front matter. Output will be utf-8 encoded.
    """
    console = Console()
    name = name or resource_name

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Support stdin
    if not source and not path:
        if not sys.stdin.isatty():
            source = [sys.stdin.buffer.read()]  # type: ignore

    # Validate input
    if not source and not path:
        message = 'Providing "source" or "path" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Create dialect
    dialect_obj = factory.create_dialect(
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
    detector_obj = factory.create_detector(
        buffer_size=buffer_size,
        sample_size=sample_size,
        field_type=field_type,
        field_names=field_names,
        field_confidence=field_confidence,
        field_float_numbers=field_float_numbers,
        field_missing_values=field_missing_values,
        schema_sync=schema_sync,
    )

    # Create resource
    resource = Resource(
        source,
        path=path,
        scheme=scheme,
        format=format,
        datatype=type or "",
        compression=compression,
        innerpath=innerpath,
        encoding=encoding,
        dialect=dialect_obj,
        schema=schema,
        basepath=basepath,
        detector=detector_obj,
    )

    # Create filter
    filter: Optional[IFilterFunction] = None
    if valid:
        filter = lambda row: row.valid
    if invalid:
        filter = lambda row: not row.valid

    # Create processor
    process: Optional[IProcessFunction] = None
    if yaml or json:
        process = lambda row: row.to_dict(json=True)
    if csv:
        process = lambda row: row.to_dict(csv=True)

    # Extract data
    try:
        data = resource.extract(
            name=name,
            filter=filter,
            process=process,
            limit_rows=limit_rows,
        )
    except Exception as exception:
        if debug:
            console.print_exception(show_locals=True)
            raise typer.Exit(1)
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Yaml mode
    if yaml:
        content = platform.yaml.safe_dump(data, allow_unicode=True).strip()
        typer.secho(content)
        raise typer.Exit()

    # Json mode
    if json:
        content = pyjson.dumps(data, indent=2, ensure_ascii=False)
        typer.echo(content)
        raise typer.Exit()

    # TODO: rework
    # Csv mode
    if csv:
        if len(data) > 1:
            note = 'For the "csv" mode you need to provide a resource "name'
            typer.secho(note, err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        options = {}
        items = list(data.values())[0]
        if items:
            labels = list(items[0].keys())
            if dialect and keep_delimiter:
                options = resource.dialect.get_control("csv").to_descriptor()
            for index, item in enumerate(items):
                if index == 0:
                    typer.secho(helpers.stringify_csv_string(labels, **options))  # type: ignore
                typer.secho(helpers.stringify_csv_string(item.values(), **options))  # type: ignore
        raise typer.Exit()

    # Default mode
    max_fields = 10
    for title, items in data.items():
        if items:
            view = Table(title=title)
            labels = list(items[0].keys())
            for label in labels[:max_fields]:
                view.add_column(label)
            if len(labels) > max_fields:
                view.add_column("...")
            for item in items:
                values = list(map(str, item.values()))
                row = values[:max_fields]
                if len(values) > max_fields:
                    row.append("...")
                view.add_row(*row)
            console.print(view)
