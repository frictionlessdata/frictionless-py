from typer import Argument, Option
from .. import config

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

scheme = Option(
    default=None,
    help="Specify scheme  [default: inferred]",
)

format = Option(
    default=None,
    help="Specify format  [default: inferred]",
)

hashing = Option(
    default=None,
    help="Specify hashing algorithm  [default: inferred]",
)

encoding = Option(
    default=None,
    help="Specify encoding  [default: inferred]",
)

innerpath = Option(
    default=None,
    help="Specify in-archive path  [default: first]",
)

compression = Option(
    default=None,
    help="Specify compression  [default: inferred]",
)

# Layout

header_rows = Option(
    default=None,
    help="Comma-separated row numbers [default: inferred]",
)

header_join = Option(
    default=None,
    help="Multiline header joiner [default: inferred]",
)

pick_fields = Option(
    default=None,
    help='Comma-separated fields to pick e.g. "1,name1"',
)

skip_fields = Option(
    default=None,
    help='Comma-separated fields to skip e.g. "2,name2"',
)

limit_fields = Option(
    default=None,
    help='Limit fields by this integer e.g. "10"',
)

offset_fields = Option(
    default=None,
    help='Offset fields by this integer e.g "5"',
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

offset_rows = Option(
    default=None,
    help='Offset rows by this integer e.g. "50"',
)

# Schema

schema = Option(
    default=None,
    help="Specify a path to a schema",
)

# Stats

stats = Option(
    default=None,
    help="Infer stats",
)

stats_hash = Option(
    default=None,
    help="Expected hash based on hashing option",
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
    default=config.DEFAULT_BUFFER_SIZE,
    help="Limit the amount of bytes to be extracted as a buffer",
)

sample_size = Option(
    default=config.DEFAULT_SAMPLE_SIZE,
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
    default=config.DEFAULT_FIELD_CONFIDENCE,
    help=(
        "Infer confidence. A float from 0 to 1. "
        "If 1, (sampled) data is guaranteed to be valid against the inferred schema"
    ),
)

field_float_numbers = Option(
    default=config.DEFAULT_FLOAT_NUMBERS,
    help="Make number floats instead of decimals",
)

field_missing_values = Option(
    default=f'"{",".join(config.DEFAULT_MISSING_VALUES)}"',
    help="Comma-separated list of missing values",
)

schema_sync = Option(
    default=None,
    help="Sync the schema based on headers",
)

# Command

basepath = Option(
    default=None,
    help="Basepath of the resource/package",
)

expand = Option(
    default=None,
    help="Expand default values",
)

original = Option(
    default=None,
    help="Don't call infer on resources",
)

parallel = Option(
    default=None,
    help="Enable multiprocessing",
)

pick_errors = Option(
    default=None,
    help='Comma-separated errors to pick e.g. "type-error"',
)

skip_errors = Option(
    default=None,
    help='Comma-separated errors to skip e.g. "blank-row"',
)

limit_errors = Option(
    default=None,
    help="Limit errors by this integer",
)

limit_memory = Option(
    default=None,
    help="Limit memory by this integer in MB",
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
