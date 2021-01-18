import sys
import petl
import typer
from typing import List
from typer import Option as Opt
from typer import Argument as Arg
from ..validate import validate
from ..layout import Layout
from .main import program
from .. import helpers


@program.command(name="validate")
def program_validate(
    source: List[str] = Arg(None, help="Data source to describe [default: stdin]"),
    type: str = Opt(None, help='Specify source type e.g. "package"'),
    # File
    scheme: str = Opt(None, help="Specify schema  [default: inferred]"),
    format: str = Opt(None, help="Specify format  [default: inferred]"),
    hashing: str = Opt(None, help="Specify hashing algorithm  [default: inferred]"),
    encoding: str = Opt(None, help="Specify encoding  [default: inferred]"),
    innerpath: str = Opt(None, help="Specify in-archive path  [default: first]"),
    compression: str = Opt(None, help="Specify compression  [default: inferred]"),
    # Layout
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
    # Schema
    schema: str = Opt(None, help="Specify a path to a schema"),
    sync_schema: bool = Opt(None, help="Sync the schema based on headers"),
    # Infer
    infer_type: str = Opt(None, help="Force all the fields to have this type"),
    infer_names: str = Opt(None, help="Comma-separated list of field names"),
    infer_volume: int = Opt(None, help="Limit data sample size by this integer"),
    infer_confidence: float = Opt(None, help="A float from 0 to 1"),
    infer_missing_values: str = Opt(None, help="Comma-separated list of missing values"),
    # Package/Resource
    basepath: str = Opt(None, help="Basepath of the resource/package"),
    parallel: bool = Opt(None, help="Enable multiprocessing"),
    # Validation
    checksum_hash: str = Opt(None, help="Expected hash based on hashing option"),
    checksum_bytes: int = Opt(None, help="Expected size in bytes"),
    checksum_rows: int = Opt(None, help="Expected amoutn of rows"),
    pick_errors: str = Opt(None, help='Comma-separated errors to pick e.g. "type-error"'),
    skip_errors: str = Opt(None, help='Comma-separated errors to skip e.g. "blank-row"'),
    limit_errors: int = Opt(None, help="Limit errors by this integer"),
    limit_memory: int = Opt(None, help="Limit memory by this integer in MB"),
    # Output
    yaml: bool = Opt(False, help="Return in pure YAML format"),
    json: bool = Opt(False, help="Return in JSON format"),
):
    """
    Validate a data source.

    Based on the inferred data source type it will validate resource or package.
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
    pick_errors = helpers.parse_csv_string(pick_errors)
    skip_errors = helpers.parse_csv_string(skip_errors)

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

    # Prepare checksum
    checksum = (
        helpers.remove_non_values(
            dict(hash=checksum_hash, bytes=checksum_bytes, rows=checksum_rows)
        )
        or None
    )

    # Prepare options
    options = helpers.remove_non_values(
        dict(
            type=type,
            # File
            scheme=scheme,
            format=format,
            hashing=hashing,
            encoding=encoding,
            innerpath=innerpath,
            compression=compression,
            # Layout
            layout=layout,
            # Schema
            schema=schema,
            sync_schema=sync_schema,
            # Infer
            infer_type=infer_type,
            infer_names=infer_names,
            infer_volume=infer_volume,
            infer_confidence=infer_confidence,
            infer_missing_values=infer_missing_values,
            # Package/Resource
            basepath=basepath,
            parallel=parallel,
            # Validation
            checksum=checksum,
            pick_errors=pick_errors,
            skip_errors=skip_errors,
            limit_errors=limit_errors,
            limit_memory=limit_memory,
        )
    )

    # Validate source
    try:
        report = validate(source, **options)
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Return JSON
    if json:
        content = report.to_json()
        typer.secho(content)
        raise typer.Exit()

    # Return YAML
    if yaml:
        content = report.to_yaml().strip()
        typer.secho(content)
        raise typer.Exit()

    # Return report
    if report.errors:
        content = []
        if is_stdin:
            source = "stdin"
        typer.secho("---")
        typer.secho(f"invalid: {source}", bold=True)
        typer.secho("---")
        for error in report.errors:
            content.append([error.code, error.message])
        typer.secho(
            str(
                petl.util.vis.lookall(
                    [["code", "message"]] + content, vrepr=str, style="simple"
                )
            )
        )

    # Return tables
    prev_invalid = False
    for number, task in enumerate(report.tasks, start=1):
        if number != 1 and prev_invalid:
            typer.secho("")
        prefix = "valid" if task.valid else "invalid"
        source = task.resource.path
        if is_stdin:
            source = "stdin"
        typer.secho("---")
        typer.secho(f"{prefix}: {source}", bold=True)
        typer.secho("---")
        if task.errors:
            prev_invalid = True
            typer.secho("")
            content = []
            for error in task.errors:
                content.append(
                    [
                        error.get("rowPosition"),
                        error.get("fieldPosition"),
                        error.code,
                        error.message,
                    ]
                )
            typer.secho(
                str(
                    petl.util.vis.lookall(
                        [["row", "field", "code", "message"]] + content,
                        vrepr=str,
                        style="simple",
                    )
                )
            )

    # Return retcode
    raise typer.Exit(code=int(not report.valid))
