import typer
from tabulate import tabulate
from .main import program
from . import common
from .. import helpers
from ..layout import Layout
from ..resource import Resource


@program.command(name="summary")
def program_summary(source: str = common.source):
    """Summary of data source.

    It will return schema, sample of the data and validation report for the resource.
    """
    # Validate input
    if not source:
        message = 'Providing "source" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)
    # Infer Resource
    try:
        resource = Resource(source, layout=Layout(limit_rows=5))
        resource.infer()
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)
    # Describe data
    content = [
        [field.name, field.type, True if field.required else ""]
        for field in resource.schema.fields
    ]
    typer.secho("")
    typer.secho("# Describe ", bold=True)
    typer.secho("")
    typer.secho(tabulate(content, headers=["name", "type", "required"], tablefmt="grid"))
    # Extract data
    try:
        resource.extract()
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)
    typer.secho("")
    typer.secho("# Extract ", bold=True)
    typer.secho("")
    typer.secho(resource.to_view())
    # Validate data
    try:
        report = resource.validate()
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)
    error_content = []
    error_list = {}
    typer.secho("")
    typer.secho("# Validate ", bold=True)
    typer.secho("")
    for task in report.tasks:
        tabular = task.resource.profile == "tabular-data-resource"
        prefix = "valid" if task.valid else "invalid"
        suffix = "" if tabular else "(non-tabular)"
        source = task.resource.path or task.resource.name
        # for zipped resources append file name
        if task.resource.innerpath:
            source = f"{source} => {task.resource.innerpath}"
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        typer.secho(f"# {prefix}: {source} {suffix}", bold=True)
        typer.secho(f"# {'-'*len(prefix)}", bold=True)
        for error in report.tasks[0].errors:
            error_content.append(
                [
                    error.get("rowPosition", ""),
                    error.get("fieldPosition", ""),
                    error.code,
                    error.message,
                ]
            )
            # error list for summary
            error_title = f"{error.name} ({error.code})"
            if error_title not in error_list:
                error_list[error_title] = 0
            error_list[error_title] += 1
            if task.partial:
                last_row_checked = error.get("rowPosition", "")
    error_content = helpers.wrap_text_to_colwidths(error_content)
    rows_checked = last_row_checked if task.partial else None
    summary_content = helpers.validation_summary(
        source,
        basepath=task.resource.basepath,
        time_taken=task.time,
        rows_checked=rows_checked,
        error_list=error_list,
    )
    typer.secho("")
    typer.secho("## Summary ", bold=True)
    typer.secho("")
    typer.secho(
        str(
            tabulate(
                summary_content,
                headers=["Description", "Size/Name/Count"],
                tablefmt="grid",
            )
        )
    )
    if len(error_content) > 0:
        typer.secho("")
        typer.secho("## Errors ", bold=True)
        typer.secho("")
        typer.secho(
            tabulate(
                error_content,
                headers=["row", "field", "code", "message"],
                tablefmt="grid",
            )
        )

    # Return retcode
    raise typer.Exit(code=int(not report.valid))
