from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, List, Optional

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .. import helpers
from ..checklist import Check, Checklist
from ..detector import Detector
from ..dialect import Dialect
from ..exception import FrictionlessException
from ..pipeline import Pipeline, Step
from ..platform import platform

if TYPE_CHECKING:
    from ..resource import Resource


# Source


def create_source(source: Any, *, path: Optional[str] = None) -> Any:
    # Support stdin
    if source is None and path is None:
        if not sys.stdin.isatty():
            return sys.stdin.buffer.read()

    # Normalize
    if isinstance(source, list) and len(source) == 1:  # type: ignore
        return source[0]  # type: ignore

    return source  # type: ignore


# Dialect


def create_dialect(
    *,
    descriptor: Optional[str] = None,
    header_rows: Optional[str] = None,
    header_join: Optional[str] = None,
    comment_char: Optional[str] = None,
    comment_rows: Optional[str] = None,
    sheet: Optional[str] = None,
    table: Optional[str] = None,
    keys: Optional[str] = None,
    keyed: Optional[bool] = None,
    csv_delimiter: Optional[str] = None,
) -> Optional[Dialect]:
    formats = platform.frictionless_formats

    # Dialect
    descriptor = helpers.parse_json_string(descriptor)
    dialect = Dialect.from_descriptor(descriptor) if descriptor else Dialect()

    # Header rows
    if header_rows is not None:
        dialect.header_rows = helpers.parse_csv_string_typed(header_rows, convert=int)

    # Header join
    if header_join is not None:
        dialect.header_join = header_join

    # Comment char
    if comment_char is not None:
        dialect.comment_char = comment_char

    # Comment rows
    if comment_rows is not None:
        dialect.comment_rows = helpers.parse_csv_string_typed(comment_rows, convert=int)

    # Controls
    if sheet is not None:
        dialect.controls.append(formats.ExcelControl(sheet=sheet))
    elif table is not None:
        dialect.controls.append(formats.SqlControl(table=table))
    elif keys is not None or keyed is not None:
        dialect.controls.append(
            formats.JsonControl.from_options(
                keys=helpers.parse_csv_string_typed(keys) if keys else None,
                keyed=keyed,
            )
        )
    elif csv_delimiter is not None:
        dialect.controls.append(
            formats.CsvControl.from_options(
                delimiter=csv_delimiter,
            )
        )

    return dialect


# Detector


def create_detector(
    *,
    buffer_size: Optional[int] = None,
    sample_size: Optional[int] = None,
    field_type: Optional[str] = None,
    field_names: Optional[str] = None,
    field_confidence: Optional[float] = None,
    field_float_numbers: Optional[bool] = None,
    field_missing_values: Optional[str] = None,
    schema_sync: Optional[bool] = None,
) -> Detector:
    # Detector
    detector = Detector()

    # Buffer size
    if buffer_size is not None:
        detector.buffer_size = buffer_size

    # Sample size
    if sample_size is not None:
        detector.sample_size = sample_size

    # Field type
    if field_type is not None:
        detector.field_type = field_type

    # Field names
    if field_names is not None:
        detector.field_names = helpers.parse_csv_string_typed(field_names)

    # Field confidence
    if field_confidence is not None:
        detector.field_confidence = field_confidence

    # Field float numbers
    if field_float_numbers is not None:
        detector.field_float_numbers = field_float_numbers

    # Field missing values
    if field_missing_values is not None:
        detector.field_missing_values = helpers.parse_csv_string_typed(
            field_missing_values
        )

    # Schema sync
    if schema_sync is not None:
        detector.schema_sync = schema_sync

    return detector


# Checklist


def create_checklist(
    *,
    descriptor: Optional[str] = None,
    checks: Optional[str] = None,
    pick_errors: Optional[str] = None,
    skip_errors: Optional[str] = None,
):
    # Checklist
    descriptor = helpers.parse_json_string(descriptor)
    checklist = Checklist.from_descriptor(descriptor) if descriptor else Checklist()

    # Checks
    for check in helpers.parse_descriptors_string(checks) or []:
        checklist.add_check(Check.from_descriptor(check))

    # Pick errors
    if pick_errors is not None:
        checklist.pick_errors = helpers.parse_csv_string_typed(pick_errors)

    # Skip errors
    if skip_errors is not None:
        checklist.skip_errors = helpers.parse_csv_string_typed(skip_errors)

    return checklist


# Pipeline


def create_pipeline(
    descriptor: Optional[str] = None,
    steps: Optional[str] = None,
):
    # Pipeline
    descriptor = helpers.parse_json_string(descriptor)
    pipeline = Pipeline.from_descriptor(descriptor) if descriptor else Pipeline()

    # Steps
    for step in helpers.parse_descriptors_string(steps) or []:
        pipeline.add_step(Step.from_descriptor(step))

    return pipeline


# Index


def index_resource(
    console: Console,
    *,
    resource: Resource,
    database: str,
    fast: bool = False,
    use_fallback: bool = False,
    qsv_path: Optional[str] = None,
    debug: bool = False,
) -> List[str]:
    # Ensure type
    if not isinstance(resource, platform.frictionless_resources.Indexable):
        note = f'Resource with data type "{resource.datatype}" is not indexable'
        raise FrictionlessException(note)

    # Index resource
    try:
        timer = helpers.Timer()
        if "://" not in database:
            database = f"sqlite:///{database}"
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            redirect_stdout=not debug,
            redirect_stderr=not debug,
            transient=True,
        ) as progress:
            status = progress.add_task(
                description=f"\\[[bold]{resource.name}[/]] Indexing...", total=None
            )
            on_progress = lambda name, message: progress.update(  # type: ignore
                status, description=f"\\[[bold]{name}[/]] Indexed {message}"
            )
            names = resource.index(
                database_url=database,
                on_progress=on_progress,  # type: ignore
                fast=fast,
                use_fallback=use_fallback,
                qsv_path=qsv_path,
            )
        console.print(f"{progress.tasks[status].description} in {timer.time} seconds")
        return names
    except Exception as exception:
        if debug:
            print_exception(console, exception=exception, debug=debug)
            raise typer.Exit(code=1)
        console.print(f"\\[{resource.name}] errored")
        return []


# Console


def print_success(console: Console, *, note: str, title: str = "Success") -> None:
    panel = Panel(note, title=title, border_style="green", title_align="left")
    console.print(panel)


def print_error(console: Console, *, note: str, title: str = "Error") -> None:
    panel = Panel(note, title=title, border_style="red", title_align="left")
    console.print(panel)


def print_exception(
    console: Console,
    *,
    exception: Exception,
    debug: Optional[bool] = False,
) -> None:
    if debug:
        console.print_exception()
        return
    text = escape(str(exception))
    panel = Panel(text, title="Error", border_style="red", title_align="left")
    console.print(panel)
