import sys
import petl
import typer
import json as pyjson
import yaml as pyyaml
from typing import List
from ..detector import Detector
from ..extract import extract
from ..layout import Layout
from .main import program
from .. import helpers
from . import common


@program.command(name="extract")
def program_extract(
    # Source
    source: List[str] = common.source,
    type: str = common.type,
    # File
    scheme: str = common.scheme,
    format: str = common.format,
    hashing: str = common.hashing,
    encoding: str = common.encoding,
    innerpath: str = common.innerpath,
    compression: str = common.compression,
    # Control
    control: str = common.control,
    # Dialect
    dialect: str = common.dialect,
    # Layout
    header_rows: str = common.header_rows,
    header_join: str = common.header_join,
    pick_fields: str = common.pick_fields,
    skip_fields: str = common.skip_fields,
    limit_fields: int = common.limit_fields,
    offset_fields: int = common.offset_fields,
    pick_rows: str = common.pick_rows,
    skip_rows: str = common.skip_rows,
    limit_rows: int = common.limit_rows,
    offset_rows: int = common.offset_rows,
    # Schema
    schema: str = common.schema,
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
    basepath: str = common.basepath,
    yaml: bool = common.yaml,
    json: bool = common.json,
    csv: bool = common.csv,
):
    """
    Extract a data source.

    Based on the inferred data source type it will return resource or package data.
    Default output format is tabulated with a front matter.
    """

    # Support stdin
    is_stdin = False
    if not source:
        is_stdin = True
        source = [sys.stdin.buffer.read()]

    # Normalize parameters
    source = list(source) if len(source) > 1 else source[0]
    control = helpers.parse_json_string(control)
    dialect = helpers.parse_json_string(dialect)
    header_rows = helpers.parse_csv_string(header_rows, convert=int)
    pick_fields = helpers.parse_csv_string(pick_fields, convert=int, fallback=True)
    skip_fields = helpers.parse_csv_string(skip_fields, convert=int, fallback=True)
    pick_rows = helpers.parse_csv_string(pick_rows, convert=int, fallback=True)
    skip_rows = helpers.parse_csv_string(skip_rows, convert=int, fallback=True)
    field_names = helpers.parse_csv_string(field_names)
    field_missing_values = helpers.parse_csv_string(field_missing_values)

    # Prepare layout
    layout = (
        Layout(
            header_rows=header_rows,
            header_join=header_join,
            pick_fields=pick_fields,
            skip_fields=skip_fields,
            limit_fields=limit_fields,
            offset_fields=offset_fields,
            pick_rows=pick_rows,
            skip_rows=skip_rows,
            limit_rows=limit_rows,
            offset_rows=offset_rows,
        )
        or None
    )

    # Prepare detector
    detector = Detector(
        **helpers.remove_non_values(
            dict(
                buffer_size=buffer_size,
                sample_size=sample_size,
                field_type=field_type,
                field_names=field_names,
                field_confidence=field_confidence,
                field_float_numbers=field_float_numbers,
                field_missing_values=field_missing_values,
                schema_sync=schema_sync,
            )
        )
    )

    # Prepare options
    options = helpers.remove_non_values(
        dict(
            type=type,
            # Spec
            scheme=scheme,
            format=format,
            hashing=hashing,
            encoding=encoding,
            innerpath=innerpath,
            compression=compression,
            control=control,
            dialect=dialect,
            layout=layout,
            schema=schema,
            # Extra
            basepath=basepath,
            detector=detector,
        )
    )

    # Extract data
    try:
        process = (lambda row: row.to_dict(json=True)) if json or yaml else None
        data = extract(source, process=process, **options)
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Normalize data
    normdata = data
    if isinstance(data, list):
        normdata = {source: data}

    # Return JSON
    if json:
        content = pyjson.dumps(data, indent=2, ensure_ascii=False)
        typer.secho(content)
        raise typer.Exit()

    # Return YAML
    if yaml:
        content = pyyaml.safe_dump(data).strip()
        typer.secho(content)
        raise typer.Exit()

    # Return CSV
    if csv:
        for number, rows in enumerate(normdata.values(), start=1):
            for row in rows:
                if row.row_number == 1:
                    typer.secho(helpers.stringify_csv_string(row.field_names))
                typer.secho(row.to_str())
            if number < len(normdata):
                typer.secho("")
        raise typer.Exit()

    # Return default
    for number, (name, rows) in enumerate(normdata.items(), start=1):
        if is_stdin:
            name = "stdin"
        prefix = "data"
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        typer.secho(f"# {prefix}: {name}", bold=True)
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        typer.secho("")
        subdata = helpers.rows_to_data(rows)
        typer.secho(str(petl.util.vis.lookall(subdata, vrepr=str, style="simple")))
        if number < len(normdata):
            typer.secho("")
