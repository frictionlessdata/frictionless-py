import sys
import typer
from typing import List
from ..actions import describe
from ..detector import Detector
from ..dialect import Dialect
from .main import program
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
    hashing: str = common.hashing,
    encoding: str = common.encoding,
    innerpath: str = common.innerpath,
    compression: str = common.compression,
    # Dialect
    dialect: str = common.dialect,
    header_rows: str = common.header_rows,
    header_join: str = common.header_join,
    comment_rows: str = common.comment_rows,
    control: str = common.control,
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
):
    """
    Describe a data source.

    Based on the inferred data source type it will return resource or package descriptor.
    Default output format is YAML with a front matter.
    """

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
        return Dialect.from_options(
            header_rows=helpers.parse_csv_string(header_rows, convert=int),
            header_join=header_join,
            comment_rows=helpers.parse_csv_string(comment_rows, convert=int),
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

    # Describe source
    try:
        metadata = describe(
            prepare_source(),
            type=type,
            # Standard
            path=path,
            scheme=scheme,
            format=format,
            hashing=hashing,
            encoding=encoding,
            innerpath=innerpath,
            compression=compression,
            dialect=prepare_dialect() or None,
            # Software
            detector=prepare_detector() or None,
            basepath=basepath,
            stats=stats,
        )
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Return JSON
    if json:
        descriptor = metadata.to_json()
        typer.secho(descriptor)
        raise typer.Exit()

    # Return YAML
    if yaml:
        descriptor = metadata.to_yaml().strip()
        typer.secho(descriptor)
        raise typer.Exit()

    # Return default
    name = " ".join(source)
    if is_stdin:
        name = "stdin"
    prefix = "metadata"
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
    typer.secho(f"# {prefix}: {name}", bold=True)
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
    typer.secho("")
    typer.secho(metadata.to_yaml().strip())
    typer.secho("")
