import sys
import petl
import typer
from typing import List
from ..validate import validate
from ..detector import Detector
from ..layout import Layout
from .main import program
from .. import helpers
from . import common


@program.command(name="validate")
def program_validate(
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
    # Stats
    stats_hash: str = common.stats_hash,
    stats_bytes: int = common.stats_bytes,
    stats_fields: int = common.stats_fields,
    stats_rows: int = common.stats_rows,
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
    pick_errors: str = common.pick_errors,
    skip_errors: str = common.skip_errors,
    limit_errors: int = common.limit_errors,
    limit_memory: int = common.limit_memory,
    original: bool = common.original,
    parallel: bool = common.parallel,
    yaml: bool = common.yaml,
    json: bool = common.json,
):
    """
    Validate a data source.

    Based on the inferred data source type it will validate resource or package.
    Default output format is YAML with a front matter.
    """

    # Support stdin
    is_stdin = False
    if not source and not path:
        if not sys.stdin.isatty():
            is_stdin = True
            source = [sys.stdin.buffer.read()]

    # Validate input
    if not source and not path:
        message = 'Providing "source" or "path" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Normalize parameters
    source = list(source) if len(source) > 1 else (source[0] if source else None)
    control = helpers.parse_json_string(control)
    dialect = helpers.parse_json_string(dialect)
    header_rows = helpers.parse_csv_string(header_rows, convert=int)
    pick_fields = helpers.parse_csv_string(pick_fields, convert=int, fallback=True)
    skip_fields = helpers.parse_csv_string(skip_fields, convert=int, fallback=True)
    pick_rows = helpers.parse_csv_string(pick_rows, convert=int, fallback=True)
    skip_rows = helpers.parse_csv_string(skip_rows, convert=int, fallback=True)
    field_names = helpers.parse_csv_string(field_names)
    field_missing_values = helpers.parse_csv_string(field_missing_values)
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

    # Prepare stats
    stats = (
        helpers.remove_non_values(
            dict(
                hash=stats_hash,
                bytes=stats_bytes,
                fields=stats_fields,
                rows=stats_rows,
            )
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
            path=path,
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
            stats=stats,
            # Extra
            basepath=basepath,
            detector=detector,
            pick_errors=pick_errors,
            skip_errors=skip_errors,
            limit_errors=limit_errors,
            limit_memory=limit_memory,
            original=original,
            parallel=parallel,
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
        prefix = "invalid"
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        typer.secho(f"# {prefix}: {source}", bold=True)
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
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
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        typer.secho(f"# {prefix}: {source}", bold=True)
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        if task.errors:
            prev_invalid = True
            typer.secho("")
            content = []
            for error in task.errors:
                content.append(
                    [
                        error.get("rowPosition", ""),
                        error.get("fieldPosition", ""),
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
