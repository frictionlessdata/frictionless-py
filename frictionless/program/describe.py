import click
import simplejson
from ..describe import describe
from .main import program


# NOTE: rewrite this function
@program.command(name="describe")
@click.argument("source", type=click.Path(), nargs=-1, required=True)
@click.option("--source-type", type=str, help="Source type")
@click.option("--json", is_flag=True, help="Output report as JSON")
# File
@click.option("--scheme", type=str, help="File scheme")
@click.option("--format", type=str, help="File format")
@click.option("--hashing", type=str, help="File hashing")
@click.option("--encoding", type=str, help="File encoding")
@click.option("--compression", type=str, help="File compression")
@click.option("--compression-path", type=str, help="File compression path")
# Schema
@click.option("--sync-schema", is_flag=True, help="Sync schema")
# Infer
@click.option("--infer-type", type=str, help="Infer type")
@click.option("--infer-names", type=str, multiple=True, help="Infer names")
@click.option("--infer-sample", type=int, help="Infer sample")
@click.option("--infer-confidence", type=float, help="Infer confidence")
@click.option("--infer-missing-values", type=str, multiple=True, help="Infer missing")
# Package/Resource
@click.option("--basepath", type=str, help="Package basepath")
def program_describe(source, *, source_type, json, **options):
    """Describe data
    \f
    API      | Usage
    -------- | --------
    Public   | `$ frictionless describe`
    """
    for key, value in list(options.items()):
        if not value:
            del options[key]
        elif isinstance(value, tuple):
            options[key] = list(value)
    source = list(source) if len(source) > 1 else source[0]
    try:
        metadata = describe(source, source_type=source_type, **options)
    except Exception as exception:
        click.secho(str(exception), err=True)
        exit(1)
    if json:
        return click.secho(simplejson.dumps(metadata, indent=2, ensure_ascii=False))
    if isinstance(source, list):
        source = " ".join(source)
    click.secho(f"[metadata] {source}", bold=True)
    click.secho("")
    click.secho(metadata.to_yaml().strip())
