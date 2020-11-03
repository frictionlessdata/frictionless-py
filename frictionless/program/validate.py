import petl
import click
import simplejson
from ..validate import validate
from .main import program


# NOTE: rewrite this function
@program.command(name="validate")
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
# Table
@click.option("--headers", type=int, multiple=True, help="Headers")
@click.option("--schema", type=click.Path(), help="Schema")
@click.option("--sync-schema", is_flag=True, help="Sync schema")
@click.option("--infer-type", type=str, help="Infer type")
@click.option("--infer-names", type=str, multiple=True, help="Infer names")
@click.option("--infer-sample", type=int, help="Infer sample")
@click.option("--infer-confidence", type=float, help="Infer confidence")
@click.option("--infer-missing-values", type=str, multiple=True, help="Infer missing")
# Validation
@click.option("--checksum-hash", type=str, help="Expected hash based on hashing option")
@click.option("--checksum-bytes", type=int, help="Expected size in bytes")
@click.option("--checksum-rows", type=int, help="Expected size in bytes")
@click.option("--pick-errors", type=str, multiple=True, help="Pick errors")
@click.option("--skip-errors", type=str, multiple=True, help="Skip errors")
@click.option("--limit-errors", type=int, help="Limit errors")
@click.option("--limit-memory", type=int, help="Limit memory")
# Package/Resource
@click.option("--basepath", type=str, help="Package basepath")
@click.option("--trusted", type=str, help="Don't fail on unsafe paths")
@click.option("--noinfer", is_flag=True, help="Validate metadata as it is")
def program_validate(source, *, source_type, json, **options):
    """Validate data
    \f
    API      | Usage
    -------- | --------
    Public   | `$ frictionless validate`
    """
    for key, value in list(options.items()):
        if not value:
            del options[key]
        elif isinstance(value, tuple):
            options[key] = list(value)
    source = list(source) if len(source) > 1 else source[0]
    try:
        report = validate(source, source_type=source_type, **options)
    except Exception as exception:
        click.secho(str(exception), err=True)
        exit(1)

    # Json
    if json:
        return click.secho(simplejson.dumps(report, indent=2, ensure_ascii=False))

    # Report
    if report.errors:
        content = []
        click.secho(f"[invalid] {source}", bold=True)
        click.secho("")
        for error in report.errors:
            content.append([error.code, error.message])
        click.secho(
            str(
                petl.util.vis.lookall(
                    [["code", "message"]] + content, vrepr=str, style="simple"
                )
            )
        )

    # Tables
    prev_invalid = False
    for number, table in enumerate(report.tables, start=1):
        if number != 1 and prev_invalid:
            click.secho("")
        prefix = "valid" if table.valid else "invalid"
        click.secho(f"[{prefix}] {table.path}", bold=True)
        if table.errors:
            prev_invalid = True
            click.secho("")
            content = []
            for error in table.errors:
                content.append(
                    [
                        error.get("rowPosition"),
                        error.get("fieldPosition"),
                        error.code,
                        error.message,
                    ]
                )
            click.secho(
                str(
                    petl.util.vis.lookall(
                        [["row", "field", "code", "message"]] + content,
                        vrepr=str,
                        style="simple",
                    )
                )
            )

    # Retcode
    exit(int(not report.valid))
