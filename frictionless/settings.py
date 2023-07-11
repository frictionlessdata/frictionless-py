from __future__ import annotations

import json
import os

# Version

VERSION = "5.15.0"

# General

UNDEFINED = object()
NAME_PATTERN = "^([-a-z0-9._/])+$"
TYPE_PATTERN = "^([-a-z/])+$"
PACKAGE_PATH = "datapackage.json"
COMPRESSION_FORMATS = ["zip", "gz"]

# Defaults

DEFAULT_STANDARDS = "v2"
DEFAULT_TYPE = "file"
DEFAULT_ENCODING = "utf-8"
DEFAULT_INNERPATH = ""
DEFAULT_PACKAGE_INNERPATH = "datapackage.json"
DEFAULT_COMPRESSION = ""
DEFAULT_BASEPATH = ""
DEFAULT_TRUSTED = False
DEFAULT_ONERROR = "ignore"
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
DEFAULT_FIELD_TYPE = "any"
DEFAULT_FIELD_TYPE_SPECS_V1 = "string"
DEFAULT_FIELD_FORMAT = "default"
DEFAULT_TRUE_VALUES = ["true", "True", "TRUE", "1"]
DEFAULT_FALSE_VALUES = ["false", "False", "FALSE", "0"]
DEFAULT_DATETIME_PATTERN = "%Y-%m-%dT%H:%M:%S%z"
DEFAULT_DATE_PATTERN = "%Y-%m-%d"
DEFAULT_TIME_PATTERN = "%H:%M:%S%z"
DEFAULT_BARE_NUMBER = True
DEFAULT_FLOAT_NUMBER = False
DEFAULT_GROUP_CHAR = ""
DEFAULT_DECIMAL_CHAR = "."
DEFAULT_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/54.0.2840.87 Safari/537.36"
    )
}
DEFAULT_FIELD_CANDIDATES = [
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

# Entities

METADATA_TRAITS = {
    "catalog": {
        "names": ["catalog.json", "catalog.yaml"],
        "props": ["packages"],
    },
    "chart": {
        "names": ["chart.json", "chart.yaml"],
        "props": ["layers", "mark"],
    },
    "package": {
        "names": ["package.json", "package.yaml"],
        "props": ["resources"],
    },
    "resource": {
        "names": ["resource.json", "resource.yaml"],
        "props": ["path", "data"],
    },
    "dialect": {
        "names": ["dialect.json", "dialect.yaml"],
        # TODO: remove csv/json/excel after #1506
        "props": ["header", "headerRows", "csv", "json", "excel"],
    },
    "jsonschema": {
        "names": ["jsonschema.json", "jsonschema.yaml"],
        "props": ["$schema"],
    },
    "schema": {
        "names": ["schema.json", "schema.yaml"],
        "props": ["fields"],
    },
    "checklist": {
        "names": ["checklist.json", "checklist.yaml"],
        "props": ["checks"],
    },
    "pipeline": {
        "names": ["pipeline.json", "pipeline.yaml"],
        "props": ["steps"],
    },
    "report": {
        "names": ["report.json", "report.yaml"],
        "props": ["errors"],
    },
    "inquiry": {
        "names": ["inquiry.json", "inquiry.yaml"],
        "props": ["tasks"],
    },
    "view": {
        "names": ["view.json", "view.yaml"],
        "props": ["query"],
    },
    "map": {
        "names": ["map.json", "map.yaml"],
        "props": ["features", "objects"],
    },
}

# Profiles


def read(*paths: str, encoding: str = "utf-8"):
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, *paths), encoding=encoding) as file:
        return file.read().strip()


GEOJSON_PROFILE = json.loads(read("assets", "profiles", "geojson.json"))
TOPOJSON_PROFILE = json.loads(read("assets", "profiles", "topojson.json"))
