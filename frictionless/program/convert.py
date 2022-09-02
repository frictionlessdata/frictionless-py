import typer
from .program import program
from ..checklist import Checklist
from ..dialect import Dialect
from ..inquiry import Inquiry
from ..package import Package
from ..pipeline import Pipeline
from ..resource import Resource
from ..report import Report
from ..schema import Schema
from ..detector import Detector
from ..system import system
from . import common


@program.command(name="convert")
def program_convert(
    # Source
    source: str = common.source,
    # Command
    path: str = common.output_path,
    json: bool = common.json,
    yaml: bool = common.yaml,
    er_diagram: bool = common.er_diagram,
    markdown: bool = common.markdown,
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """Convert metadata to various output"""

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Validate input
    if not source:
        message = 'Providing "source" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Initialize metadata
    metadata = None
    metadata_type = Detector.detect_descriptor(source)
    try:
        if metadata_type == "package":
            metadata = Package.from_descriptor(source)
        elif metadata_type == "resource":
            metadata = Resource.from_descriptor(source)
        elif metadata_type == "schema":
            metadata = Schema.from_descriptor(source)
        elif metadata_type == "checklist":
            metadata = Checklist.from_descriptor(source)
        elif metadata_type == "dialect":
            metadata = Dialect.from_descriptor(source)
        elif metadata_type == "report":
            metadata = Report.from_descriptor(source)
        elif metadata_type == "inquiry":
            metadata = Inquiry.from_descriptor(source)
        elif metadata_type == "detector":
            metadata = Detector.from_descriptor(source)
        elif metadata_type == "pipeline":
            metadata = Pipeline.from_descriptor(source)
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise

    # Not found/supported
    if not metadata:
        message = "File not found or not supported type of metadata"
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Return json
    if json:
        content = metadata.to_json(path)
        typer.secho(content)
        raise typer.Exit()

    # Return yaml
    if yaml:
        content = metadata.to_yaml(path)
        typer.secho(content)
        raise typer.Exit()

    # Return ER Diagram
    if er_diagram:
        if not isinstance(metadata, Package):
            message = "ER-diagram format is only available for package"
            typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        content = metadata.to_er_diagram(path)
        typer.secho(content)
        raise typer.Exit()

    # Return markdown
    if markdown:
        content = metadata.to_markdown(path)
        typer.secho(content)
        raise typer.Exit()

    # Return retcode
    message = "No format specified. For example --yaml"
    typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
    raise typer.Exit(1)
