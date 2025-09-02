import platform as python_platform
import sys
from functools import cached_property
from importlib import import_module
from typing import Any, Callable, ClassVar


def extras(*, name: str):
    """Extra dependency decorator"""

    def outer(func: Callable[..., Any]):
        def inner(*args: Any, **kwargs: Any):
            try:
                return func(*args, **kwargs)
            except Exception:
                module = import_module("frictionless.exception")
                note = f'Please install "frictionless[{name}]"'
                raise module.FrictionlessException(note)

        return inner

    return outer


class Platform:
    """Platform representation"""

    type: ClassVar[str] = python_platform.system().lower()
    """
    Type of the platform(OS) framework is running on. For example, windows,
    linux etc.
    """

    python: ClassVar[str] = f"{sys.version_info.major}.{sys.version_info.minor}"
    """
    Python version
    """

    # Core

    @cached_property
    def bz2(self):
        import bz2

        return bz2

    @cached_property
    def chardet(self):
        import chardet

        return chardet

    @cached_property
    def dateutil_parser(self):
        import dateutil.parser

        return dateutil.parser

    @cached_property
    def frictionless(self):
        import frictionless

        return frictionless

    @cached_property
    def frictionless_checks(self):
        import frictionless.checks

        return frictionless.checks

    @cached_property
    def frictionless_errors(self):
        import frictionless.errors

        return frictionless.errors

    @cached_property
    def frictionless_fields(self):
        import frictionless.fields

        return frictionless.fields

    @cached_property
    def frictionless_formats(self):
        import frictionless.formats

        return frictionless.formats

    @cached_property
    def frictionless_portals(self):
        import frictionless.portals

        return frictionless.portals

    @cached_property
    def frictionless_resources(self):
        import frictionless.resources

        return frictionless.resources

    @cached_property
    def frictionless_schemes(self):
        import frictionless.schemes

        return frictionless.schemes

    @cached_property
    def frictionless_steps(self):
        import frictionless.steps

        return frictionless.steps

    @cached_property
    def gzip(self):
        import gzip

        return gzip

    @cached_property
    def html_parser(self):
        import html.parser

        return html.parser

    @cached_property
    def isodate(self):
        import isodate  # type: ignore

        return isodate

    @cached_property
    def jinja2(self):
        import jinja2

        return jinja2

    @cached_property
    def jinja2_filters(self):
        import jinja2.filters

        return jinja2.filters

    @cached_property
    def jsonschema(self):
        import jsonschema

        return jsonschema

    @cached_property
    def jsonschema_validators(self):
        import jsonschema.validators

        return jsonschema.validators

    @cached_property
    def lzma(self):
        import lzma

        return lzma

    @cached_property
    def marko(self):
        import marko

        return marko

    @cached_property
    def marko_ext_gfm(self):
        import marko.ext.gfm

        return marko.ext.gfm

    @cached_property
    def petl(self):
        import petl  # type: ignore

        return petl

    @cached_property
    def psycopg(self):
        import psycopg

        return psycopg

    @cached_property
    def requests(self):
        import requests

        return requests

    @cached_property
    def requests_utils(self):
        import requests.utils

        return requests.utils

    @cached_property
    def rfc3986(self):
        import rfc3986  # type: ignore

        return rfc3986

    @cached_property
    def validators(self):
        import validators  # type: ignore

        return validators

    @cached_property
    def yaml(self):
        import yaml

        return yaml

    @cached_property
    def zipfile(self):
        import zipfile

        return zipfile

    # Extras

    @cached_property
    @extras(name="aws")
    def boto3(self):
        import boto3  # type: ignore

        return boto3

    @cached_property
    @extras(name="ckan")
    def frictionless_ckan_mapper_ckan_to_frictionless(self):
        import frictionless_ckan_mapper.ckan_to_frictionless  # type: ignore

        return frictionless_ckan_mapper.ckan_to_frictionless

    @cached_property
    @extras(name="ckan")
    def frictionless_ckan_mapper_frictionless_to_ckan(self):
        import frictionless_ckan_mapper.frictionless_to_ckan  # type: ignore

        return frictionless_ckan_mapper.frictionless_to_ckan

    @cached_property
    @extras(name="excel")
    def xlrd(self):
        import xlrd  # type: ignore

        return xlrd

    @cached_property
    @extras(name="excel")
    def xlwt(self):
        import xlwt  # type: ignore

        return xlwt

    @cached_property
    @extras(name="excel")
    def openpyxl(self):
        import openpyxl

        return openpyxl

    @cached_property
    @extras(name="excel")
    def tableschema_to_template(self):
        import tableschema_to_template  # type: ignore

        return tableschema_to_template

    @cached_property
    @extras(name="json")
    def ijson(self):
        import ijson  # type: ignore

        return ijson

    @cached_property
    @extras(name="json")
    def jsonlines(self):
        import jsonlines

        return jsonlines

    @cached_property
    @extras(name="github")
    def github(self):
        import github

        return github

    @cached_property
    @extras(name="gsheets")
    def pygsheets(self):
        import pygsheets  # type: ignore

        return pygsheets

    @cached_property
    @extras(name="html")
    def pyquery(self):
        import pyquery  # type: ignore

        return pyquery

    @cached_property
    @extras(name="ods")
    def ezodf(self):
        import ezodf  # type: ignore

        return ezodf

    @cached_property
    @extras(name="markdown")
    def livemark(self):
        import livemark  # type: ignore

        return livemark

    @cached_property
    @extras(name="pandas")
    def pandas(self):
        import pandas  # type: ignore

        return pandas

    @cached_property
    @extras(name="polars")
    def polars(self):
        import polars  # type: ignore

        return polars

    @cached_property
    @extras(name="pandas")
    def pandas_core_dtypes_api(self):
        import pandas.core.dtypes.api  # type: ignore

        return pandas.core.dtypes.api

    @cached_property
    @extras(name="pandas")
    def numpy(self):
        import numpy

        return numpy

    @cached_property
    @extras(name="parquet")
    def fastparquet(self):
        import fastparquet  # type: ignore

        return fastparquet

    @cached_property
    @extras(name="spss")
    def sav_reader_writer(self):
        import savReaderWriter  # type: ignore

        return savReaderWriter

    @cached_property
    @extras(name="sql")
    def sqlalchemy(self):
        import sqlalchemy

        return sqlalchemy

    @cached_property
    @extras(name="sql")
    def sqlalchemy_exc(self):
        import sqlalchemy.exc

        return sqlalchemy.exc

    @cached_property
    @extras(name="sql")
    def sqlalchemy_schema(self):
        import sqlalchemy.schema

        return sqlalchemy.schema

    @cached_property
    @extras(name="sql")
    def sqlalchemy_dialects(self):
        import sqlalchemy.dialects

        return sqlalchemy.dialects

    @cached_property
    @extras(name="sql")
    def sqlalchemy_dialects_postgresql(self):
        import sqlalchemy.dialects.postgresql

        return sqlalchemy.dialects.postgresql

    @cached_property
    @extras(name="sql")
    def sqlalchemy_dialects_mysql(self):
        import sqlalchemy.dialects.mysql

        return sqlalchemy.dialects.mysql

    @cached_property
    @extras(name="zenodo")
    def pyzenodo3(self):
        import pyzenodo3  # type: ignore

        return pyzenodo3

    @cached_property
    @extras(name="zenodo")
    def pyzenodo3_upload(self):
        import pyzenodo3.upload  # type: ignore

        return pyzenodo3.upload

    @cached_property
    @extras(name="wkt")
    def wkt(self):
        import frictionless.vendors.wkt

        return frictionless.vendors.wkt


platform = Platform()
