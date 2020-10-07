import click
from ..transform import transform
from .main import program


@program.command(name="transform")
@click.argument("source", type=click.Path(), required=True)
def program_transform(source):
    """Transform data
    \f
    API      | Usage
    -------- | --------
    Public   | `$ frictionless transform`
    """
    try:
        transform(source)
    except Exception as exception:
        click.secho(str(exception), err=True)
        exit(1)
