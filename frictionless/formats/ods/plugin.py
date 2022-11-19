from __future__ import annotations
from ...system import Plugin
from ...resource import Resource
from .adapter import OdsAdapter
from .control import OdsControl
from .parser import OdsParser


class OdsPlugin(Plugin):
    """Plugin for ODS"""

    # Hooks

    def create_adapter(self, source, *, control=None):
        if isinstance(source, str):
            resource = Resource(path=source)
            resource.infer(sample=False)
            if resource.format == "ods":
                control = control or OdsControl()
                return OdsAdapter(control, resource=resource)  # type: ignore

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
