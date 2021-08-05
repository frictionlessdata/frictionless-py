import os
import json
import gzip
import zipfile


# Helpers


def read_asset(*paths):
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, "assets", *paths)) as file:
        return file.read().strip()


# General


UNDEFINED = object()
VERSION = read_asset("VERSION")
COMPRESSION_FORMATS = ["zip", "gz"]
INQUIRY_PROFILE = json.loads(read_asset("profiles", "inquiry.json"))
PIPELINE_PROFILE = json.loads(read_asset("profiles", "pipeline.json"))
REPORT_PROFILE = json.loads(read_asset("profiles", "report.json"))
STATUS_PROFILE = json.loads(read_asset("profiles", "status.json"))
SCHEMA_PROFILE = json.loads(read_asset("profiles", "schema", "general.json"))
RESOURCE_PROFILE = json.loads(read_asset("profiles", "resource", "general.json"))
TABULAR_RESOURCE_PROFILE = json.loads(read_asset("profiles", "resource", "tabular.json"))
PACKAGE_PROFILE = json.loads(read_asset("profiles", "package", "general.json"))
FISCAL_PACKAGE_PROFILE = json.loads(read_asset("profiles", "package", "fiscal.json"))
TABULAR_PACKAGE_PROFILE = json.loads(read_asset("profiles", "package", "tabular.json"))
GEOJSON_PROFILE = json.loads(read_asset("profiles", "geojson", "general.json"))
TOPOJSON_PROFILE = json.loads(read_asset("profiles", "geojson", "topojson.json"))


# Defaults


DEFAULT_SCHEME = "file"
DEFAULT_FORMAT = "csv"
DEFAULT_HASHING = "md5"
DEFAULT_ENCODING = "utf-8"
DEFAULT_INNERPATH = ""
DEFAULT_COMPRESSION = ""
DEFAULT_HEADER = True
DEFAULT_HEADER_ROWS = [1]
DEFAULT_HEADER_JOIN = " "
DEFAULT_HEADER_CASE = True
DEFAULT_FLOAT_NUMBERS = False
DEFAULT_MISSING_VALUES = [""]
DEFAULT_LIMIT_ERRORS = 1000
DEFAULT_LIMIT_MEMORY = 1000
DEFAULT_BUFFER_SIZE = 10000
DEFAULT_SAMPLE_SIZE = 100
DEFAULT_ENCODING_CONFIDENCE = 0.5
DEFAULT_FIELD_CONFIDENCE = 0.9
DEFAULT_PACKAGE_PROFILE = "data-package"
DEFAULT_RESOURCE_PROFILE = "data-resource"
DEFAULT_TABULAR_RESOURCE_PROFILE = "tabular-data-resource"
DEFAULT_TRUE_VALUES = ["true", "True", "TRUE", "1"]
DEFAULT_FALSE_VALUES = ["false", "False", "FALSE", "0"]
DEFAULT_DATETIME_PATTERN = "%Y-%m-%dT%H:%M:%S%z"
DEFAULT_DATE_PATTERN = "%Y-%m-%d"
DEFAULT_TIME_PATTERN = "%H:%M:%S%z"
DEFAULT_BARE_NUMBER = True
DEFAULT_FLOAT_NUMBER = False
DEFAULT_GROUP_CHAR = ""
DEFAULT_DECIMAL_CHAR = "."
DEFAULT_SERVER_PORT = 8000
DEFAULT_CANDIDATES = [
    {"type": "yearmonth"},
    {"type": "geopoint"},
    {"type": "duration"},
    {"type": "geojson"},
    {"type": "object"},
    {"type": "array"},
    {"type": "datetime"},
    {"type": "time"},
    {"type": "date"},
    {"type": "integer"},
    {"type": "number"},
    {"type": "boolean"},
    {"type": "year"},
    {"type": "string"},
]


# Backports


# It can be removed after dropping support for Python 3.6 and Python 3.7
COMPRESSION_EXCEPTIONS = (
    (zipfile.BadZipFile, gzip.BadGzipFile)
    if hasattr(gzip, "BadGzipFile")
    else (zipfile.BadZipFile)
)
