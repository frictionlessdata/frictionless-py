import sys
import typer
from typing import List
from ..describe import describe
from ..detector import Detector
from ..layout import Layout
from .main import program
from .. import helpers
from . import common


@program.command(name="describe")
def program_describe(
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
    # Stats
    stats: bool = common.stats,
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
    expand: bool = common.expand,
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
    if not source:
        is_stdin = True
        source = [helpers.create_byte_stream(sys.stdin.buffer.read())]

    # Normalize parameters
    source = list(source) if len(source) > 1 else source[0]
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
            layout=layout,
            # Extra
            detector=detector,
            expand=expand,
            stats=stats,
        )
    )

    # Describe source
    try:
        metadata = describe(source, **options)
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
    if is_stdin:
        source = "stdin"
    elif isinstance(source, list):
        source = " ".join(source)
    prefix = "metadata"
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
    typer.secho(f"# {prefix}: {source}", bold=True)
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
    typer.secho("")
    typer.secho(metadata.to_yaml().strip())
    typer.secho("")
