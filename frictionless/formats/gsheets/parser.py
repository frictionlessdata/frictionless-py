from __future__ import annotations
import re
from ...resource import Parser
from ...resource import Resource
from ...exception import FrictionlessException
from .control import GsheetsControl
from ... import helpers
from ... import errors


class GsheetsParser(Parser):
    """Google Sheets parser implementation."""

    supported_types = [
        "string",
    ]

    # Read

    def read_cell_stream_create(self):
        normpath = self.resource.normpath
        match = re.search(r".*/d/(?P<key>[^/]+)/.*?(?:gid=(?P<gid>\d+))?$", normpath)
        normpath = "https://docs.google.com/spreadsheets/d/%s/export?format=csv&id=%s"
        key, gid = "", ""
        if match:
            key = match.group("key")
            gid = match.group("gid")
        normpath = normpath % (key, key)
        if gid:
            normpath = "%s&gid=%s" % (normpath, gid)
        with Resource(path=normpath, stats=self.resource.stats) as resource:
            yield from resource.cell_stream

    # Write

    def write_row_stream(self, source):
        normpath = self.resource.normpath
        pygsheets = helpers.import_from_extras("pygsheets", name="gsheets")
        control = GsheetsControl.from_dialect(self.resource.dialect)
        match = re.search(r".*/d/(?P<key>[^/]+)/.*?(?:gid=(?P<gid>\d+))?$", normpath)
        if not match:
            error = errors.FormatError(note=f"Cannot save {normpath}")
            raise FrictionlessException(error)
        key = match.group("key")
        gid = match.group("gid")
        gc = pygsheets.authorize(service_account_file=control.credentials)
        sh = gc.open_by_key(key)
        wks = sh.worksheet_by_id(gid) if gid else sh[0]
        data = []
        with source:
            data.append(source.schema.field_names)
            for row in source.row_stream:
                data.append(row.to_list())
        wks.update_values("A1", data)
        return normpath
