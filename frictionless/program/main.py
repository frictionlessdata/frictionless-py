import click
from .. import config


@click.group(name="frictionless")
@click.version_option(config.VERSION, message="%(version)s", help="Print version")
def program():
    """Describe, extract, validate and transform tabular data.
    \f
    API      | Usage
    -------- | --------
    Public   | `$ frictionless`
    """
    pass
