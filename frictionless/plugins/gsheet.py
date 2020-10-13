import re
from ..plugin import Plugin
from ..parser import Parser
from ..system import system
from ..dialects import Dialect
from ..resource import Resource
from .. import exceptions
from .. import errors


# Plugin


class GsheetPlugin(Plugin):
    """Plugin for Google Sheets

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheet import GsheetPlugin`

    """

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "gsheet":
            return GsheetDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "gsheet":
            return GsheetParser(resource)


# Dialect


class GsheetDialect(Dialect):
    """Gsheet dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheet import GsheetDialect`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    pass


# Parser


class GsheetParser(Parser):
    """Google Sheets parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheet import GsheetParser`

    """

    loading = False

    # Read

    def read_data_stream_create(self):
        source = self.resource.source
        match = re.search(r".*/d/(?P<key>[^/]+)/.*?(?:gid=(?P<gid>\d+))?$", source)
        source = "https://docs.google.com/spreadsheets/d/%s/export?format=csv&id=%s"
        key, gid = "", ""
        if match:
            key = match.group("key")
            gid = match.group("gid")
        source = source % (key, key)
        if gid:
            source = "%s&gid=%s" % (source, gid)
        resource = Resource.from_source(source, stats=self.resource.stats)
        with system.create_parser(resource) as parser:
            yield from parser.data_stream

    # Write

    def write(self, read_row_stream):
        error = errors.Error(note="Writing to Google Sheets is not supported")
        raise exceptions.FrictionlessException(error)
