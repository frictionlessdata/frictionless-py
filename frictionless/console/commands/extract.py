from __future__ import annotations

import json as pyjson
from typing import TYPE_CHECKING, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from ...exception import FrictionlessException
from ...helpers import stringify_csv_string
from ...platform import platform
from ...resource import Resource
from ...system import system
from .. import common, helpers
from ..console import console

if TYPE_CHECKING:
    from ... import types


DEFAULT_MAX_FIELDS = 10
DEFAULT_MAX_ROWS = 10


@console.command(name="extract")
def console_extract(
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
    valid: bool = common.valid_rows,
    invalid: bool = common.invalid_rows,
    limit_rows: int = common.limit_rows,
    yaml: bool = common.yaml,
    json: bool = common.json,
    csv: bool = common.csv,
    # System
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
    # Deprecated
    resource_name: str = common.resource_name,
    keep_delimiter: bool = common.keep_delimiter,
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
            schema_sync=schema_sync,
        )

        # Create filter
        filter: Optional[types.IFilterFunction] = None
        if valid:
            filter = lambda row: row.valid
        elif invalid:
            filter = lambda row: not row.valid

        # Create processor
        process: Optional[types.IProcessFunction] = None
        if yaml or json:
            process = lambda row: row.to_dict(json=True)
        elif csv:
            process = lambda row: row.to_dict(csv=True)

        # Create limit
        if limit_rows is None:  # type: ignore
            if not any([yaml, json, csv]):
                limit_rows = DEFAULT_MAX_ROWS

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
            detector=detector_obj,
        )

        # Add dialect
        if dialect_obj:
            resource.dialect = dialect_obj

        # Ensure type
        if not isinstance(resource, platform.frictionless_resources.Extractable):
            note = f'Resource with data type "{resource.datatype}" is not extractable'
            raise FrictionlessException(note)

        # Extract data
        data = resource.extract(
            name=name,
            filter=filter,
            process=process,
            limit_rows=limit_rows,
        )

        # List resources
        resources = resource.list()
    except Exception as exception:
        helpers.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Yaml mode
    if yaml:
        content = platform.yaml.safe_dump(data, allow_unicode=True).strip()
        print(content)
        raise typer.Exit()

    # Json mode
    if json:
        content = pyjson.dumps(data, indent=2, ensure_ascii=False)
        print(content)
        raise typer.Exit()

    # No data
    if not data:
        note = "No tabular data have been found in the source"
        helpers.print_error(console, note=note)
        raise typer.Exit(code=1)

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
                options.pop("type", None)
            for index, item in enumerate(items):
                if index == 0:
                    typer.secho(stringify_csv_string(labels, **options))  # type: ignore
                typer.secho(stringify_csv_string(item.values(), **options))  # type: ignore
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

    console.rule("[bold]Tables")
    for title, items in data.items():
        # Empty
        if not items:
            helpers.print_error(console, note="No rows found", title="Empty")
            continue

        # General
        # TODO: rework
        view = Table(title=title)
        labels = list(items[0].keys())
        for label in labels[:DEFAULT_MAX_FIELDS]:
            view.add_column(label)
        if len(labels) > DEFAULT_MAX_FIELDS:
            view.add_column("...")
        for item in items:
            values = list(map(str, item.values()))
            row = values[:DEFAULT_MAX_FIELDS]
            if len(values) > DEFAULT_MAX_FIELDS:
                row.append("...")
            view.add_row(*row)
        if len(items) == limit_rows == DEFAULT_MAX_ROWS:
            row = ["..."] * min(len(labels), DEFAULT_MAX_FIELDS)
            if len(labels) > DEFAULT_MAX_FIELDS:
                row.append("...")
            view.add_row(*row)
        console.print(view)
