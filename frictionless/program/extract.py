from __future__ import annotations
import sys
import typer
import json as pyjson
from typing import List
from ..platform import platform
from ..detector import Detector
from ..dialect import Dialect
from ..actions import extract
from ..system import system
from .program import program
from .. import formats
from .. import helpers
from . import common


@program.command(name="extract")
def program_extract(
    # Source
    source: List[str] = common.source,
    type: str = common.type,
    # File
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
    comment_rows: str = common.skip_rows,
    sheet: str = common.sheet,
    table: str = common.table,
    keys: str = common.keys,
    keyed: bool = common.keyed,
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
    # Software
    basepath: str = common.basepath,
    resource_name: str = common.resource_name,
    valid: bool = common.valid_rows,
    invalid: bool = common.invalid_rows,
    limit_rows: int = common.limit_rows,
    yaml: bool = common.yaml,
    json: bool = common.json,
    csv: bool = common.csv,
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
    descriptor: str = common.descriptor,
    keep_delimiter: bool = common.keep_delimiter,
):
    """
    Extract a data source.

    Based on the inferred data source type it will return resource or package data.
    Default output format is tabulated with a front matter. Output will be utf-8 encoded.
    """

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Support stdin
    is_stdin = False
    if not source and not path and not descriptor:
        if not sys.stdin.isatty():
            is_stdin = True
            source = [sys.stdin.buffer.read()]  # type: ignore

    # Validate input
    if not source and not path and not descriptor:
        message = 'Providing "source" or "path" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Prepare source
    def prepare_source():
        return list(source) if len(source) > 1 else (source[0] if source else None)

    # Prepare dialect
    def prepare_dialect():
        dialect_descriptor = helpers.parse_json_string(dialect)
        if dialect_descriptor:
            return Dialect.from_descriptor(dialect_descriptor)
        controls = []
        if sheet:
            controls.append(formats.ExcelControl(sheet=sheet))
        elif table:
            controls.append(formats.SqlControl(table=table))
        elif keys or keyed:
            controls.append(
                formats.JsonControl.from_options(
                    keys=helpers.parse_csv_string(keys),
                    keyed=keyed,
                )
            )
        return Dialect.from_options(
            header_rows=helpers.parse_csv_string(header_rows, convert=int),
            header_join=header_join,
            comment_char=comment_char,
            comment_rows=helpers.parse_csv_string(comment_rows, convert=int),
            controls=controls,
        )

    # Prepare detector
    def prepare_detector():
        return Detector.from_options(
            buffer_size=buffer_size,
            sample_size=sample_size,
            field_type=field_type,
            field_names=helpers.parse_csv_string(field_names),
            field_confidence=field_confidence,
            field_float_numbers=field_float_numbers,
            field_missing_values=helpers.parse_csv_string(field_missing_values),
            schema_sync=schema_sync,
        )

    # Prepare process
    def prepare_process():
        if json or yaml:
            return lambda row: row.to_dict(json=True)

    # Prepare filter
    def prepare_filter():
        if valid:
            return lambda row: row.valid
        if invalid:
            return lambda row: not row.valid

    # Prepare options
    def prepare_options():
        return dict(
            type=type,
            # Standard
            path=path,
            scheme=scheme,
            format=format,
            encoding=encoding,
            innerpath=innerpath,
            compression=compression,
            dialect=prepare_dialect(),
            schema=schema,
            # Software
            basepath=basepath,
            detector=prepare_detector(),
            # Action
            descriptor=descriptor,
            resource_name=resource_name,
            limit_rows=limit_rows,
            process=prepare_process(),
            filter=prepare_filter(),
        )

    # Extract data
    try:
        data = extract(prepare_source(), **prepare_options())
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise

    # Normalize data
    normdata = data
    if isinstance(data, list):
        normdata = {prepare_source(): data}  # type: ignore

    # Return JSON
    if json:
        content = pyjson.dumps(data, indent=2, ensure_ascii=False)
        typer.secho(content)
        raise typer.Exit()

    # Return YAML
    if yaml:
        content = platform.yaml.safe_dump(data, allow_unicode=True).strip()
        typer.secho(content)
        raise typer.Exit()

    # Return CSV
    # TODO: rework
    if csv:
        options = {}
        if dialect and keep_delimiter:
            options = prepare_dialect().to_dict().get("csv")
        for number, rows in enumerate(normdata.values(), start=1):  # type: ignore
            for index, row in enumerate(rows):
                if index == 0:
                    typer.secho(helpers.stringify_csv_string(row.field_names, **options))  # type: ignore
                typer.secho(row.to_str(**options))  # type: ignore
            if number < len(normdata):  # type: ignore
                typer.secho("")
        raise typer.Exit()

    # Return default
    for number, (name, rows) in enumerate(normdata.items(), start=1):  # type: ignore
        if is_stdin:
            name = "stdin"
        prefix = "data"
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        typer.secho(f"# {prefix}: {name}", bold=True)
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        typer.secho("")
        subdata = helpers.rows_to_data(rows)
        if len(subdata) <= 0:
            valid_text = "valid" if valid else "invalid"
            typer.secho(str(f"No {valid_text} rows"))
            continue
        typer.secho(str(platform.petl.util.vis.lookall(subdata, vrepr=str, style="simple")))  # type: ignore
        if number < len(normdata):  # type: ignore
            typer.secho("")
