import typer
from .main import program


@program.command(name="describe")
def program_describe(
    source: str = typer.Argument(..., help="Describe source"),
    source_type: str = typer.Option(None, help="Source type"),
    json: bool = typer.Option(False, help="Output as JSON"),
    # File
    scheme: str = typer.Option(None, help="Scheme"),
    format: str = typer.Option(None, help="Format"),
    hashing: str = typer.Option(None, help="Hashing"),
    encoding: str = typer.Option(None, help="Encoding"),
    compression: str = typer.Option(None, help="Compression"),
    compression_path: str = typer.Option(None, help="Compression path"),
    # Control/Dialect/Query/Header
    pick_fields: str = typer.Option(
        None, help='Comma-separated fields to pick e.g. "1,name"'
    ),
    skip_fields: str = typer.Option(
        None, help='Comma-separated fields to skip e.g. "2,other_name"'
    ),
    limit_fields: int = typer.Option(None, help="Limit fields"),
    offset_fields: int = typer.Option(None, help="Offset fields"),
    # Infer
    # Description
    expand: bool = typer.Option(False, help="Expand default values"),
):
    """
    Create a new user with USERNAME.
    """
    typer.echo("Describe")
