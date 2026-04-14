from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ...system import Plugin
from .control import ParquetControl
from .parser import ParquetParser

if TYPE_CHECKING:
    from ...resource import Resource


class ParquetPlugin(Plugin):
    """Plugin for Parquet"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format == "parq" or resource.format == "parquet":
            return ParquetParser(resource)

    def matches_datatype(self, resource: Resource):
        if resource.format in ["parq", "parquet"]:
            return "table"

    def detect_resource(self, resource: Resource):
        if resource.format in ["parq", "parquet"]:
            resource.mediatype = resource.mediatype or "application/parquet"

    def select_control_class(self, type: Optional[str] = None):
        if type == "parquet":
            return ParquetControl
