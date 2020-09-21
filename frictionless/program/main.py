import click
from .. import config


@click.group(name="frictionless")
@click.version_option(config.VERSION, message="%(version)s", help="Print version")
def program():
    """Main program

    API      | Usage
    -------- | --------
    Public   | `$ frictionless`

    """
    pass
