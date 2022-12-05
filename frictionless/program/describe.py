from __future__ import annotations
import sys
import typer
from typing import List
from ..detector import Detector
from ..actions import describe
from ..dialect import Dialect
from ..system import system
from .program import program
from .. import formats
from .. import helpers
from . import common


@program.command(name="describe")
def program_describe(
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
    comment_rows: str = common.comment_rows,
    sheet: str = common.sheet,
    table: str = common.table,
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
    stats: bool = common.stats,
    yaml: bool = common.yaml,
    json: bool = common.json,
    markdown: bool = common.markdown,
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """
    Describe a data source.

    Based on the inferred data source type it will return resource or package descriptor.
    Default output format is YAML with a front matter.
    """

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Support stdin
    is_stdin = False
    if not source and not path:
        if not sys.stdin.isatty():
            is_stdin = True
            source = [sys.stdin.buffer.read()]  # type: ignore

    # Validate input
    if not source and not path:
        message = 'Providing "source" or "path" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Prepare source
    def prepare_source():
        return list(source) if len(source) > 1 else (source[0] if source else None)

    # Prepare dialect
    def prepare_dialect():
        descriptor = helpers.parse_json_string(dialect)
        if descriptor:
            return Dialect.from_descriptor(descriptor)
        controls = []
        if sheet:
            controls.append(formats.ExcelControl(sheet=sheet))
        elif table:
            controls.append(formats.SqlControl(table=table))
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
        )

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
            # Software
            detector=prepare_detector(),
            basepath=basepath,
            stats=stats,
        )

    # Describe source
    try:
        metadata = describe(prepare_source(), **prepare_options())
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise

    # Return JSON
    if json:
        output = metadata.to_json()
        typer.secho(output)
        raise typer.Exit()

    # Return YAML
    if yaml:
        output = metadata.to_yaml().strip()
        typer.secho(output)
        raise typer.Exit()

    # Return Markdown
    if markdown:
        output = metadata.to_markdown().strip()
        typer.secho(output)
        raise typer.Exit()

    # Return default
    name = " ".join(source)
    prefix = "metadata"
    name = "stdin" if is_stdin else " ".join(source)
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
    typer.secho(f"# {prefix}: {name}", bold=True)
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
    typer.secho("")
    typer.secho(metadata.to_yaml().strip())
    typer.secho("")
