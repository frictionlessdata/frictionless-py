from __future__ import annotations
from ...system import Plugin
from ...resource import Resource
from ...records import PathDetails
from .adapter import OdsAdapter
from .control import OdsControl
from .parser import OdsParser


class OdsPlugin(Plugin):
    """Plugin for ODS"""

    # Hooks

    def create_adapter(self, source, *, control=None):
        if isinstance(source, str):
            resource = Resource(path=source)
            if resource.format == "ods":
                control = control or OdsControl()
                return OdsAdapter(control, resource=resource)  # type: ignore

    def create_parser(self, resource):
        if resource.format == "ods":
            return OdsParser(resource)

    def detect_path_details(self, details: PathDetails):
        if details.format == "ods":
            details.type = "table"
            details.mediatype = "application/vnd.oasis.opendocument.spreadsheet"

    def select_Control(self, type):
        if type == "ods":
            return OdsControl
