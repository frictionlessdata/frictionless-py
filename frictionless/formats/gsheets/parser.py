from __future__ import annotations
import re
from ...platform import platform
from ...system import Parser
from ...resource import Resource
from ...exception import FrictionlessException
from .control import GsheetsControl
from ... import errors


class GsheetsParser(Parser):
    """Google Sheets parser implementation."""

    supported_types = [
        "string",
    ]

    # Read

    def read_cell_stream_create(self):
        path = self.resource.normpath
        match = re.search(r".*/d/(?P<key>[^/]+)/.*?(?:gid=(?P<gid>\d+))?$", path)
        path = "https://docs.google.com/spreadsheets/d/%s/export?format=csv&id=%s"
        key, gid = "", ""
        if match:
            key = match.group("key")
            gid = match.group("gid")
        path = path % (key, key)
        if gid:
            path = "%s&gid=%s" % (path, gid)
        with Resource(path=path, stats=self.resource.stats) as resource:
            yield from resource.cell_stream

    # Write

    def write_row_stream(self, source):
        path = self.resource.normpath
        control = GsheetsControl.from_dialect(self.resource.dialect)
        match = re.search(r".*/d/(?P<key>[^/]+)/.*?(?:gid=(?P<gid>\d+))?$", path)
        if not match:
            error = errors.FormatError(note=f"Cannot save {path}")
            raise FrictionlessException(error)
        key = match.group("key")
        gid = match.group("gid")
        gc = platform.pygsheets.authorize(service_account_file=control.credentials)
        sh = gc.open_by_key(key)
        wks = sh.worksheet_by_id(gid) if gid else sh[0]  # type: ignore
        data = []
        with source:
            data.append(source.schema.field_names)
            for row in source.row_stream:
                data.append(row.to_list())
        wks.update_values("A1", data)  # type: ignore
        return path
