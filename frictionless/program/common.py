from __future__ import annotations
from typer import Argument, Option
from .. import settings

# TODO: migrate to click options to encapsulate types (or we can set types here)?

# Source

source = Argument(
    default=None,
    help="Data source [default: stdin]",
)

type = Option(
    default=None,
    help='Specify type e.g. "package"',
)

# File

path = Option(
    default=None,
    help="Specify the data path explicitly (e.g. you need to use it if your data is JSON)",
)

scheme = Option(
    default=None,
    help="Specify scheme  [default: inferred]",
)

format = Option(
    default=None,
    help="Specify format  [default: inferred]",
)

encoding = Option(
    default=None,
    help="Specify encoding  [default: inferred]. Output will be utf-8 encoded",
)

innerpath = Option(
    default=None,
    help="Specify in-archive path  [default: first]",
)

compression = Option(
    default=None,
    help="Specify compression  [default: inferred]",
)

# Dialect

header_rows = Option(
    default=None,
    help="Comma-separated row numbers [default: inferred]",
)

header_join = Option(
    default=None,
    help="Multiline header joiner [default: inferred]",
)

comment_char = Option(
    default=None,
    help='A char indicating that the row is a comment e.g. "#"',
)

comment_rows = Option(
    default=None,
    help='Comma-separated rows to be considered as comments e.g. "2,3,4,5"',
)

pick_rows = Option(
    default=None,
    help='Comma-separated rows to pick e.g. "1,<blank>"',
)

skip_rows = Option(
    default=None,
    help='Comma-separated rows to skip e.g. "2,3,4,5"',
)

limit_rows = Option(
    default=None,
    help='Limit rows by this integer e.g "100"',
)

control = Option(
    default=None,
    help="An inline JSON object or a path to a JSON file that provides the control (configuration for the data Loader)",
)

dialect = Option(
    default=None,
    help="An inline JSON object or a path to a JSON file that provides the dialect (configuration for the parser)",
)


sheet = Option(
    default=None,
    help="The sheet to use from the input data (only with XLS and ODS files/plugins)",
)

table = Option(
    default=None,
    help="The table to use from the SQL database (SQL plugin)",
)

keys = Option(
    default=None,
    help="The keys to use as column names for the Inline or JSON data plugins",
)


keyed = Option(
    default=False,
    help="Whether the input data is keyed for the Inline or JSON data plugins",
)

# Schema

schema = Option(
    default=None,
    help="Specify a path to a schema",
)

# Checklist

checklist = Option(
    default=None,
    help="An inline JSON object or a path to a JSON file that provides the checklist",
)

checks = Option(
    default=None,
    help='Validation checks e.g "duplicate-row table-dimensions:numRows=1"',
)

pick_errors = Option(
    default=None,
    help='Comma-separated errors to pick e.g. "type-error"',
)

skip_errors = Option(
    default=None,
    help='Comma-separated errors to skip e.g. "blank-row"',
)

# Pipeline

pipeline = Option(
    default=None,
    help="An inline JSON object or a path to a JSON file that provides the pipeline",
)

steps = Option(
    default=None,
    help='Tranform steps e.g "table-recast cell-set:fieldName=id:value=3"',
)

# Stats

stats = Option(
    default=None,
    help="Infer stats",
)

stats_md5 = Option(
    default=None,
    help="Expected MD5 hash",
)

stats_sha256 = Option(
    default=None,
    help="Expected SHA256 hash",
)

stats_bytes = Option(
    default=None,
    help="Expected size in bytes",
)

stats_fields = Option(
    default=None,
    help="Expected amount of fields",
)

stats_rows = Option(
    default=None,
    help="Expected amount of rows",
)

# Detector

buffer_size = Option(
    default=settings.DEFAULT_BUFFER_SIZE,
    help="Limit the amount of bytes to be extracted as a buffer",
)

sample_size = Option(
    default=settings.DEFAULT_SAMPLE_SIZE,
    help="Limit the number of rows to be extracted as a sample",
)

field_type = Option(
    default=None,
    help="Force all the fields to have this type",
)

field_names = Option(
    default=None,
    help="Comma-separated list of field names",
)

field_confidence = Option(
    default=settings.DEFAULT_FIELD_CONFIDENCE,
    help=(
        "Infer confidence. A float from 0 to 1. "
        "If 1, (sampled) data is guaranteed to be valid against the inferred schema"
    ),
)

field_float_numbers = Option(
    default=settings.DEFAULT_FLOAT_NUMBERS,
    help="Make number floats instead of decimals",
)

field_missing_values = Option(
    default=f'"{",".join(settings.DEFAULT_MISSING_VALUES)}"',
    help="Comma-separated list of missing values",
)

schema_sync = Option(
    default=None,
    help="Sync the schema based on the data's header row",
)

# Software

basepath = Option(
    default=None,
    help="Basepath of the resource/package",
)

resource_name = Option(
    default=None,
    help="Name of resource to validate",
)

valid_rows = Option(
    default=False,
    help="Return valid rows",
)

invalid_rows = Option(
    default=False,
    help="Return invalid rows",
)

limit_errors = Option(
    default=settings.DEFAULT_LIMIT_ERRORS,
    help="Limit errors by this integer",
)

limit_rows = Option(
    default=None,
    help="Limit rows by this integer",
)

parallel = Option(
    default=None,
    help="Enable multiprocessing",
)

output_path = Option(
    default=None,
    help="Specify the output file path explicitly (e.g. package.yaml)",
)

yaml = Option(
    default=False,
    help="Return in pure YAML format",
)

json = Option(
    default=False,
    help="Return in JSON format",
)

csv = Option(
    default=False,
    help="Return in CSV format",
)

markdown = Option(
    default=False,
    help="Return in Markdown format",
)

er_diagram = Option(
    default=False,
    help="Return er diagram. It is only available for package",
)

port = Option(
    settings.DEFAULT_SERVER_PORT,
    help="Specify server port",
)

debug = Option(
    default=False,
    help="Enable debug mode",
)

root = Option(
    default=False,
    help="Run server as root",
)

trusted = Option(
    default=False,
    help="Follow unsafe paths",
)

standards = Option(
    default=None,
    help="Possible options: v1, v2, v2-strict (default: v2)",
)

descriptor = Option(
    default=None,
    help="Excplicit path to the descriptor instead of guessing by providing a source",
)

keep_delimiter = Option(
    default=False,
    help="Keep input delimiter",
)

database = Option(
    default=None,
    help="Database url",
)

fast = Option(
    default=None,
    help="Fast database indexing",
)

qsv = Option(
    default=None,
    help="QSV binary path",
)

metadata = Option(
    default=False,
    help="Add metadata while indexing",
)

fallback = Option(
    default=False,
    help="If fast indexing errored fallback to the normal mode",
)
