from __future__ import annotations
import typer
from rich.console import Console
from typing import List
from tabulate import tabulate
from ..resource import Resource
from ..system import system
from .program import program
from . import common
from . import utils


@program.command(name="validate")
def program_validate(
    # Source
    source: List[str] = common.source,
    name: str = common.resource_name,
    type: str = common.type,
    path: str = common.path,
    scheme: str = common.scheme,
    format: str = common.format,
    encoding: str = common.encoding,
    innerpath: str = common.innerpath,
    compression: str = common.compression,
    schema: str = common.schema,
    hash: str = common.hash,
    bytes: int = common.bytes,
    fields: int = common.fields,
    rows: int = common.rows,
    basepath: str = common.basepath,
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
    # Detector
    buffer_size: int = common.buffer_size,
    sample_size: int = common.sample_size,
    field_type: str = common.field_type,
    field_names: str = common.field_names,
    field_confidence: float = common.field_confidence,
    field_float_numbers: bool = common.field_float_numbers,
    field_missing_values: str = common.field_missing_values,
    schema_sync: bool = common.schema_sync,
    # Checklist
    checklist: str = common.checklist,
    checks: str = common.checks,
    pick_errors: str = common.pick_errors,
    skip_errors: str = common.skip_errors,
    # Command
    parallel: bool = common.parallel,
    limit_rows: int = common.limit_rows,
    limit_errors: int = common.limit_errors,
    yaml: bool = common.yaml,
    json: bool = common.json,
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
    # Deprecated
    resource_name: str = common.resource_name,
):
    """
    Validate a data source.

    Based on the inferred data source type it will validate resource or package.
    Default output format is YAML with a front matter.
    """
    console = Console()
    name = name or resource_name

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Create source
    source = utils.create_source(source, path=path)
    if not source and not path:
        note = 'Providing "source" or "path" is required'
        utils.print_error(console, note=note)
        raise typer.Exit(code=1)

    # Create dialect
    dialect_obj = utils.create_dialect(
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
    detector_obj = utils.create_detector(
        buffer_size=buffer_size,
        sample_size=sample_size,
        field_type=field_type,
        field_names=field_names,
        field_confidence=field_confidence,
        field_float_numbers=field_float_numbers,
        field_missing_values=field_missing_values,
        schema_sync=schema_sync,
    )

    # Create checklist
    checklist_obj = utils.create_checklist(
        descriptor=checklist,
        checks=checks,
        pick_errors=pick_errors,
        skip_errors=skip_errors,
    )

    # Validate resource
    try:
        resource = Resource(
            source=utils.create_source(source),
            name=name,
            path=path,
            scheme=scheme,
            format=format,
            datatype=type or "",
            compression=compression,
            innerpath=innerpath,
            encoding=encoding,
            hash=hash,
            bytes=bytes,
            fields=fields,
            rows=rows,
            dialect=dialect_obj,
            schema=schema,
            basepath=basepath,
            detector=detector_obj,
        )
        report = resource.validate(
            checklist_obj,
            name=name,
            parallel=parallel,
            limit_rows=limit_rows,
            limit_errors=limit_errors,
        )
    except Exception as exception:
        utils.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Return JSON
    if json:
        content = report.to_json()
        print(content)
        raise typer.Exit()

    # Return YAML
    if yaml:
        content = report.to_yaml().strip()
        print(content)
        raise typer.Exit()

    # Return validation report errors
    if report.errors:
        content = []
        prefix = "invalid"
        title = "stdin" if not source else source
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        typer.secho(f"# {prefix}: {title}", bold=True)
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
