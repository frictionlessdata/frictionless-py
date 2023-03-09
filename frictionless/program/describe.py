from __future__ import annotations
import typer
from typing import List
from rich.syntax import Syntax
from rich.console import Console
from ..platform import platform
from ..resource import Resource
from ..system import system
from .program import program
from . import common
from . import utils


@program.command(name="describe")
def program_describe(
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
    # Command
    basepath: str = common.basepath,
    # TODO: allow cherry-picking stats for adding to a descriptor
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
    console = Console()
    resources = platform.frictionless_resources

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
    )

    # Describe source
    try:
        # Create resource
        metadata = Resource(
            source=utils.create_source(source),
            path=path,
            scheme=scheme,
            format=format,
            datatype=type or "",
            compression=compression,
            innerpath=innerpath,
            encoding=encoding,
            dialect=dialect_obj,
            basepath=basepath,
            detector=detector_obj,
        )

        # Infer package
        if isinstance(metadata, resources.PackageResource):
            metadata = metadata.read_metadata()
            metadata.infer(stats=stats)
            if name is not None:
                metadata = metadata.get_resource(name)

        # Infer resource
        metadata.infer(stats=stats)
        if type == "dialect":
            metadata = metadata.dialect
        elif type == "schema":
            metadata = metadata.schema
    except Exception as exception:
        utils.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Yaml mode
    if yaml:
        descriptor = metadata.to_yaml().strip()
        print(descriptor)
        raise typer.Exit()

    # Json mode
    if json:
        descriptor = metadata.to_json()
        print(descriptor)
        raise typer.Exit()

    # Markdown mode
    if markdown:
        descriptor = metadata.to_markdown().strip()
        print(descriptor)
        raise typer.Exit()

    # Default mode
    descriptor = metadata.to_yaml().strip()
    syntax = Syntax(descriptor, "yaml")
    console.print(syntax)
