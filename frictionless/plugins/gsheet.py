import re
from ..file import File
from ..plugin import Plugin
from ..parser import Parser
from ..system import system
from ..dialects import Dialect
from .. import exceptions
from .. import errors


# Plugin


class GsheetPlugin(Plugin):
    """Plugin for Google Sheets

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheet import GsheetPlugin`

    """

    def create_dialect(self, file, *, descriptor):
        if file.format == "gsheet":
            return GsheetDialect(descriptor)

    def create_parser(self, file):
        if file.format == "gsheet":
            return GsheetParser(file)


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
        source = self.file.source
        match = re.search(r".*/d/(?P<key>[^/]+)/.*?(?:gid=(?P<gid>\d+))?$", source)
        source = "https://docs.google.com/spreadsheets/d/%s/export?format=csv&id=%s"
        key, gid = "", ""
        if match:
            key = match.group("key")
            gid = match.group("gid")
        source = source % (key, key)
        if gid:
            source = "%s&gid=%s" % (source, gid)
        with system.create_parser(File(source, stats=self.file.stats)) as parser:
            yield from parser.data_stream

    # Write

    # NOTE: if we migrate to the native driver we can enable it
    def write(self, row_stream, *, schema):
        error = errors.Error(note="Writing to Google Sheets is not supported")
        raise exceptions.FrictionlessException(error)
