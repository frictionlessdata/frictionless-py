from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ...resource import Resource
from ...system import Plugin
from .adapter import OdsAdapter
from .control import OdsControl
from .parser import OdsParser

if TYPE_CHECKING:
    from ...dialect import Control


class OdsPlugin(Plugin):
    """Plugin for ODS"""

    # Hooks

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ):
        if packagify:
            if isinstance(source, str):
                resource = Resource(path=source, basepath=basepath)
                if resource.format == "ods":
                    control = control or OdsControl()
                    return OdsAdapter(control, resource=resource)  # type: ignore

    def create_parser(self, resource: Resource):
        if resource.format == "ods":
            return OdsParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format == "ods":
            resource.datatype = resource.datatype or "table"
            resource.mediatype = (
                resource.mediatype or "application/vnd.oasis.opendocument.spreadsheet"
            )

    def select_control_class(self, type: Optional[str] = None):
        if type == "ods":
            return OdsControl
