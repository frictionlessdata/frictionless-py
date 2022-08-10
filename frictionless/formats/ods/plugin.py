from __future__ import annotations
from ...plugin import Plugin
from .control import OdsControl
from .parser import OdsParser


class OdsPlugin(Plugin):
    """Plugin for ODS"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "ods":
            return OdsParser(resource)

    def detect_resource(self, resource):
        if resource.format == "ods":
            resource.type = "table"
            resource.mediatype = "application/vnd.oasis.opendocument.spreadsheet"

    def select_Control(self, type):
        if type == "ods":
            return OdsControl
