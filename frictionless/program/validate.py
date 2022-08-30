from __future__ import annotations
import sys
import typer
from typing import List
from tabulate import tabulate
from ..stats import Stats
from ..actions import validate
from ..detector import Detector
from ..checklist import Checklist, Check
from ..dialect import Dialect
from ..system import system
from .program import program
from .. import formats
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
    keys: str = common.keys,
    keyed: bool = common.keyed,
    # Schema
    schema: str = common.schema,
    # Checklist
    checklist: str = common.checklist,
    checks: str = common.checks,
    pick_errors: str = common.pick_errors,
    skip_errors: str = common.skip_errors,
    # Stats
    stats_md5: str = common.stats_md5,
    stats_sha256: str = common.stats_sha256,
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
    # Software
    basepath: str = common.basepath,
    resource_name: str = common.resource_name,
    limit_errors: int = common.limit_errors,
    limit_rows: int = common.limit_rows,
    parallel: bool = common.parallel,
    yaml: bool = common.yaml,
    json: bool = common.json,
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """
    Validate a data source.

    Based on the inferred data source type it will validate resource or package.
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
        elif keys or keyed:
            controls.append(formats.JsonControl.from_options(keys=keys, keyed=keyed))
        return Dialect.from_options(
            header_rows=helpers.parse_csv_string(header_rows, convert=int),
            header_join=header_join,
            comment_char=comment_char,
            comment_rows=helpers.parse_csv_string(comment_rows, convert=int),
            controls=controls,
        )

    # Prepare checklist
    def prepare_checklist():
        descriptor = helpers.parse_json_string(checklist)
        if descriptor:
            return Checklist.from_descriptor(descriptor)
        check_objects = []
        for check_descriptor in helpers.parse_descriptors_string(checks) or []:
            check_objects.append(Check.from_descriptor(check_descriptor))
        return Checklist.from_options(
            checks=check_objects,
            pick_errors=helpers.parse_csv_string(pick_errors),
            skip_errors=helpers.parse_csv_string(skip_errors),
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

    # Prepare stats
    def prepare_stats():
        return Stats.from_options(
            md5=stats_md5,
            sha256=stats_sha256,
            bytes=stats_bytes,
            fields=stats_fields,
            rows=stats_rows,
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
            schema=schema,
            checklist=prepare_checklist(),
            stats=prepare_stats(),
            # Software
            basepath=basepath,
            detector=prepare_detector(),
            # Action
            resource_name=resource_name,
            limit_errors=limit_errors,
            limit_rows=limit_rows,
            parallel=parallel,
        )

    # Validate source
    try:
        report = validate(prepare_source(), **prepare_options())
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise

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

    # Return validation report errors
    if report.errors:
        content = []
        prefix = "invalid"
        name = "stdin" if is_stdin else source
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        typer.secho(f"# {prefix}: {name}", bold=True)
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        for error in report.errors:
            content.append([error.type, error.message])
        typer.secho(
            str(tabulate(content, headers=["type", "message"], tablefmt="simple"))
        )

    # Return validation report summary and tables
    typer.secho(str(report.to_summary()))

    # Return retcode
    raise typer.Exit(code=int(not report.valid))
