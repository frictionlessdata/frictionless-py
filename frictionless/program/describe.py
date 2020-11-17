import sys
import typer
from typing import List
from typer import Option as Opt
from typer import Argument as Arg
from ..describe import describe
from ..query import Query
from .main import program
from .. import dialects
from .. import helpers


@program.command(name="describe")
def program_describe(
    source: List[str] = Arg(None, help="Data source to describe [default: stdin]"),
    source_type: str = Opt(None, help='Specify source type e.g. "package"'),
    # File
    scheme: str = Opt(None, help="Specify schema  [default: inferred]"),
    format: str = Opt(None, help="Specify format  [default: inferred]"),
    hashing: str = Opt(None, help="Specify hashing algorithm  [default: inferred]"),
    encoding: str = Opt(None, help="Specify encoding  [default: inferred]"),
    compression: str = Opt(None, help="Specify compression  [default: inferred]"),
    compression_path: str = Opt(None, help="Specify in-archive path  [default: first]"),
    # Control/Dialect/Query/Header
    header_rows: str = Opt(None, help="Comma-separated row numbers  [default: 1]"),
    header_join: str = Opt(None, help="A separator to join a multiline header"),
    pick_fields: str = Opt(None, help='Comma-separated fields to pick e.g. "1,name1"'),
    skip_fields: str = Opt(None, help='Comma-separated fields to skip e.g. "2,name2"'),
    limit_fields: int = Opt(None, help="Limit fields by this integer"),
    offset_fields: int = Opt(None, help="Offset fields by this integer"),
    pick_rows: str = Opt(None, help='Comma-separated rows to pick e.g. "1,<blank>"'),
    skip_rows: str = Opt(None, help='Comma-separated rows to skip e.g. "2,3,4,5"'),
    limit_rows: int = Opt(None, help="Limit rows by this integer"),
    offset_rows: int = Opt(None, help="Offset rows by this integer"),
    # Infer
    infer_type: str = Opt(None, help="Force all the fields to have this type"),
    infer_names: str = Opt(None, help="Comma-separated list of field names"),
    infer_volume: int = Opt(None, help="Limit data sample size by this integer"),
    infer_confidence: float = Opt(None, help="A float from 0 to 1"),
    infer_missing_values: str = Opt(None, help="Comma-separated list of missing values"),
    # Package/Resource
    basepath: str = Opt(None, help="Basepath of the resource/package"),
    # Description
    expand: bool = Opt(None, help="Expand default values"),
    # Output
    yaml: bool = Opt(False, help="Return in pure YAML format"),
    json: bool = Opt(False, help="Return in JSON format"),
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
    infer_names = helpers.parse_csv_string(infer_names)
    infer_missing_values = helpers.parse_csv_string(infer_missing_values)

    # Prepare dialect
    dialect = (
        dialects.Dialect(
            header_rows=header_rows,
            header_join=header_join,
        )
        or None
    )

    # Prepare query
    query = (
        Query(
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

    # Prepare options
    options = helpers.remove_non_values(
        dict(
            source_type=source_type,
            # File
            scheme=scheme,
            format=format,
            hashing=hashing,
            encoding=encoding,
            compression=compression,
            compression_path=compression_path,
            # Control/Dialect/Query/Header
            dialect=dialect,
            query=query,
            # Infer
            infer_type=infer_type,
            infer_names=infer_names,
            infer_volume=infer_volume,
            infer_confidence=infer_confidence,
            infer_missing_values=infer_missing_values,
            # Description
            expand=expand,
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
    typer.secho("---")
    typer.secho(f"metadata: {source}", bold=True)
    typer.secho("---")
    typer.secho("")
    typer.secho(metadata.to_yaml().strip())
    typer.secho("")
