import typer
from typer import Option as Opt
from typer import Argument as Arg
from .main import program


@program.command(name="describe")
def program_describe(
    source: str = Arg(..., help="Data source to describe"),
    source_type: str = Opt(None, help='Specify source type e.g. "package"'),
    json: bool = Opt(False, help="Make the output to be in JSON"),
    # File
    scheme: str = Opt(None, help="Specify schema  [default: inferred]"),
    format: str = Opt(None, help="Specify format  [default: inferred]"),
    hashing: str = Opt(None, help="Specify hashing algorithm  [default: inferred]"),
    encoding: str = Opt(None, help="Specify encoding  [default: inferred]"),
    compression: str = Opt(None, help="Specify compression  [default: inferred]"),
    compression_path: str = Opt(None, help="Specify in-archive path  [default: first]"),
    # Control/Dialect/Query/Header
    header_rows: str = Opt("1", help="Comma-separated row numbers"),
    header_join: str = Opt(None, help="A separator to join a multiline header"),
    pick_fields: str = Opt(None, help='Comma-separated fields to pick e.g. "1,name1"'),
    skip_fields: str = Opt(None, help='Comma-separated fields to skip e.g. "2,name2"'),
    limit_fields: int = Opt(None, help="Limit fields by this integer"),
    offset_fields: int = Opt(None, help="Offset fields by this integer"),
    pick_rows: str = Opt(None, help='Comma-separated rows to pick e.g. "1,<blank>"'),
    skip_rows: str = Opt(None, help='Comma-separated rows to skip e.g. "2,3,4,5"'),
    limit_rows: int = Opt(None, help="Limit rows by this integer"),
    offset_rows: int = Opt(None, help="Offset rows by this integer"),
    # Infer
    infer_type: str = Opt(None, help="Force all the fields to have this type"),
    infer_names: str = Opt(None, help="Comma-separated list of field names"),
    infer_sample: int = Opt(None, help="Limit data sample by this integer"),
    infer_confidence: float = Opt(None, help="A float from 0 to 1"),
    infer_missing_values: str = Opt(None, help="Comma-separated list of missing values"),
    # Package/Resource
    basepath: str = Opt(None, help="Basepath of the resource/package"),
    # Description
    expand: bool = Opt(False, help="Expand default values"),
):
    """
    Describe a data source.

    Based on the inferred data source type it will return
    resource or package descriptor. Default output format is YAML.
    """
    typer.echo("Describe")
