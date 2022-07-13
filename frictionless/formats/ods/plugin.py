from __future__ import annotations
from ...plugin import Plugin
from .control import OdsControl
from .parser import OdsParser


class OdsPlugin(Plugin):
    """Plugin for ODS"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "ods":
            return OdsControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "ods":
            return OdsParser(resource)

    def detect_resource(self, resource):
        if resource.format == "ods":
            resource.type = "table"
            resource.mediatype = "application/vnd.oasis.opendocument.spreadsheet"
