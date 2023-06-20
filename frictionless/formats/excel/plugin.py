from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ...resource import Resource
from ...system import Plugin
from .adapter import ExcelAdapter
from .control import ExcelControl
from .parsers import XlsParser, XlsxParser

if TYPE_CHECKING:
    from ...dialect import Control


class ExcelPlugin(Plugin):
    """Plugin for Excel"""

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
                if resource.format == "xlsx":
                    control = control or ExcelControl()
                    return ExcelAdapter(control, resource=resource)  # type: ignore

    def create_parser(self, resource: Resource):
        if resource.format == "xlsx":
            return XlsxParser(resource)
        elif resource.format == "xls":
            return XlsParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format in ["xlsx", "xls"]:
            resource.datatype = resource.datatype or "table"
            resource.mediatype = resource.mediatype or "application/vnd.ms-excel"

    def select_control_class(self, type: Optional[str] = None):
        if type == "excel":
            return ExcelControl
