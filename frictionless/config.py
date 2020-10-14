import io
import os
import json
import gzip
import zipfile


# Helpers


def read_asset(*paths):
    dirname = os.path.dirname(__file__)
    return io.open(os.path.join(dirname, "assets", *paths)).read().strip()


# General


VERSION = read_asset("VERSION")
COMPRESSION_FORMATS = ["zip", "gz"]
REMOTE_SCHEMES = ["http", "https", "ftp", "ftps"]
INQUIRY_PROFILE = json.loads(read_asset("profiles", "inquiry.json"))
REPORT_PROFILE = json.loads(read_asset("profiles", "report.json"))
SCHEMA_PROFILE = json.loads(read_asset("profiles", "schema.json"))
RESOURCE_PROFILE = json.loads(read_asset("profiles", "resource", "general.json"))
TABULAR_RESOURCE_PROFILE = json.loads(read_asset("profiles", "resource", "tabular.json"))
PACKAGE_PROFILE = json.loads(read_asset("profiles", "package", "general.json"))
FISCAL_PACKAGE_PROFILE = json.loads(read_asset("profiles", "package", "fiscal.json"))
TOPOJSON_PROFILE = json.loads(read_asset("profiles", "topojson.json"))
GEOJSON_PROFILE = json.loads(read_asset("profiles", "geojson.json"))
UNDEFINED = object()


# Defaults


DEFAULT_SCHEME = "file"
DEFAULT_FORMAT = "csv"
DEFAULT_HASHING = "md5"
DEFAULT_ENCODING = "utf-8"
DEFAULT_COMPRESSION = "no"
DEFAULT_COMPRESSION_PATH = ""
DEFAULT_HEADER = True
DEFAULT_HEADER_ROWS = [1]
DEFAULT_HEADER_JOIN = " "
DEFAULT_HEADER_CASE = True
DEFAULT_MISSING_VALUES = [""]
DEFAULT_LIMIT_MEMORY = 1000
DEFAULT_INFER_VOLUME = 100
DEFAULT_INFER_CONFIDENCE = 0.9
DEFAULT_INFER_ENCODING_VOLUME = 10000
DEFAULT_INFER_ENCODING_CONFIDENCE = 0.5
DEFAULT_RESOURCE_PROFILE = "data-resource"
DEFAULT_PACKAGE_PROFILE = "data-package"
DEFAULT_TRUE_VALUES = ["true", "True", "TRUE", "1"]
DEFAULT_FALSE_VALUES = ["false", "False", "FALSE", "0"]
DEFAULT_DATETIME_PATTERN = "%Y-%m-%dT%H:%M:%S%z"
DEFAULT_DATE_PATTERN = "%Y-%m-%d"
DEFAULT_TIME_PATTERN = "%H:%M:%S%z"
DEFAULT_BARE_NUMBER = True
DEFAULT_GROUP_CHAR = ""
DEFAULT_DECIMAL_CHAR = "."
DEFAULT_SERVER_PORT = 8000
DEFAULT_HTTP_TIMEOUT = 10
DEFAULT_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/54.0.2840.87 Safari/537.36"
    )
}


# Backports


# NOTE: Can be removed for Python3.8+
COMPRESSION_EXCEPTIONS = (
    (zipfile.BadZipFile, gzip.BadGzipFile)
    if hasattr(gzip, "BadGzipFile")
    else (zipfile.BadZipFile)
)
