import re
from ..plugin import Plugin
from ..parser import Parser
from ..system import system
from ..dialect import Dialect
from ..resource import Resource
from ..metadata import Metadata
from ..exception import FrictionlessException
from .. import helpers
from .. import errors


# Plugin


class GsheetsPlugin(Plugin):
    """Plugin for Google Sheets

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheets import GsheetsPlugin`

    """

    def create_file(self, file):
        if not file.memory:
            if "docs.google.com/spreadsheets" in file.path:
                if "export" not in file.path and "pub" not in file.path:
                    file.scheme = ""
                    file.format = "gsheets"
                elif "csv" in file.path:
                    file.scheme = "https"
                    file.format = "csv"
                return file

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "gsheets":
            return GsheetsDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "gsheets":
            return GsheetsParser(resource)


# Dialect


class GsheetsDialect(Dialect):
    """Gsheets dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheets import GsheetsDialect`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, credentials=None):
        self.setinitial("credentials", credentials)
        super().__init__(descriptor)

    @Metadata.property
    def credentials(self):
        """
        Returns:
            str: credentials
        """
        return self.get("credentials")

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "credentials": {"type": "string"},
        },
    }


# Parser


class GsheetsParser(Parser):
    """Google Sheets parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheets import GsheetsParser`

    """

    needs_loader = False

    # Read

    def read_data_stream_create(self):
        fullpath = self.resource.fullpath
        match = re.search(r".*/d/(?P<key>[^/]+)/.*?(?:gid=(?P<gid>\d+))?$", fullpath)
        fullpath = "https://docs.google.com/spreadsheets/d/%s/export?format=csv&id=%s"
        key, gid = "", ""
        if match:
            key = match.group("key")
            gid = match.group("gid")
        fullpath = fullpath % (key, key)
        if gid:
            fullpath = "%s&gid=%s" % (fullpath, gid)
        resource = Resource(path=fullpath, stats=self.resource.stats)
        with system.create_parser(resource) as parser:
            yield from parser.data_stream

    # Write

    def write_row_stream_save(self, read_row_stream):
        pygsheets = helpers.import_from_plugin("pygsheets", plugin="gsheets")
        fullpath = self.resource.fullpath
        match = re.search(r".*/d/(?P<key>[^/]+)/.*?(?:gid=(?P<gid>\d+))?$", fullpath)
        if not match:
            error = errors.FormatError(note=f"Cannot save {fullpath}")
            raise FrictionlessException(error)
        key = match.group("key")
        gid = match.group("gid")
        gc = pygsheets.authorize(service_account_file=self.resource.dialect.credentials)
        sh = gc.open_by_key(key)
        wks = sh.worksheet_by_id(gid) if gid else sh[0]
        data = []
        for row in read_row_stream():
            if row.row_number == 1:
                data.append(row.field_names)
            data.append(row.to_list())
        wks.update_values("A1", data)
        return fullpath
