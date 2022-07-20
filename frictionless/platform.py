import sys
from typing import ClassVar
from functools import cached_property
import platform as python_platform
from .helpers import extras


class Platform:
    """Platform representation"""

    type: ClassVar[str] = python_platform.system().lower()
    """TODO: add docs"""

    python: ClassVar[str] = f"{sys.version_info.major}.{sys.version_info.minor}"
    """TODO: add docs"""

    # Core

    @cached_property
    def jinja2(self):
        import jinja2

        return jinja2

    # Extras

    @cached_property
    @extras(name="api")
    def fastapi(self):
        import fastapi

        return fastapi

    @cached_property
    @extras(name="api")
    def uvicorn(self):
        import uvicorn

        return uvicorn

    @cached_property
    @extras(name="aws")
    def boto3(self):
        import boto3

        return boto3

    @cached_property
    @extras(name="bigquery")
    def googleapiclient_http(self):
        import googleapiclient.http

        return googleapiclient.http

    @cached_property
    @extras(name="bigquery")
    def googleapiclient_errors(self):
        import googleapiclient.errors

        return googleapiclient.errors

    @cached_property
    @extras(name="ckan")
    def frictionless_ckan_mapper_ckan_to_frictionless(self):
        import frictionless_ckan_mapper.ckan_to_frictionless

        return frictionless_ckan_mapper.ckan_to_frictionless

    @cached_property
    @extras(name="excel")
    def xlrd(self):
        import xlrd

        return xlrd

    @cached_property
    @extras(name="excel")
    def xlwt(self):
        import xlwt

        return xlwt

    @cached_property
    @extras(name="excel")
    def openpyxl(self):
        import openpyxl

        return openpyxl

    @cached_property
    @extras(name="excel")
    def tableschema_to_template(self):
        import tableschema_to_template

        return tableschema_to_template

    @cached_property
    @extras(name="json")
    def ijson(self):
        import ijson

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
        import pygsheets

        return pygsheets

    @cached_property
    @extras(name="html")
    def pyquery(self):
        import pyquery

        return pyquery

    @cached_property
    @extras(name="ods")
    def ezodf(self):
        import ezodf

        return ezodf

    @cached_property
    @extras(name="pandas")
    def pandas(self):
        import pandas

        return pandas

    @cached_property
    @extras(name="pandas")
    def pandas_core_dtypes_api(self):
        import pandas.core.dtypes.api

        return pandas.core.dtypes.api

    @cached_property
    @extras(name="pandas")
    def numpy(self):
        import numpy

        return numpy

    @cached_property
    @extras(name="spss")
    def sav_reader_writer(self):
        import savReaderWriter

        return savReaderWriter

    @cached_property
    @extras(name="sql")
    def sqlalchemy(self):
        import sqlalchemy

        return sqlalchemy

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
        import pyzenodo3

        return pyzenodo3


platform = Platform()
