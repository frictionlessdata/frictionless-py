import re
from ...parser import Parser
from ...system import system
from ...resource import Resource
from ...exception import FrictionlessException
from ... import helpers
from ... import errors


class GsheetsParser(Parser):
    """Google Sheets parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheets import GsheetsParser`

    """

    supported_types = [
        "string",
    ]

    # Read

    def read_list_stream_create(self):
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
            yield from parser.list_stream

    # Write

    def write_row_stream(self, resource):
        pygsheets = helpers.import_from_plugin("pygsheets", plugin="gsheets")
        source = resource
        target = self.resource
        fullpath = target.fullpath
        match = re.search(r".*/d/(?P<key>[^/]+)/.*?(?:gid=(?P<gid>\d+))?$", fullpath)
        if not match:
            error = errors.FormatError(note=f"Cannot save {fullpath}")
            raise FrictionlessException(error)
        key = match.group("key")
        gid = match.group("gid")
        gc = pygsheets.authorize(service_account_file=target.dialect.credentials)
        sh = gc.open_by_key(key)
        wks = sh.worksheet_by_id(gid) if gid else sh[0]
        data = []
        with source:
            for row in source.row_stream:
                if row.row_number == 1:
                    data.append(row.field_names)
                data.append(row.to_list())
        wks.update_values("A1", data)
        return fullpath
