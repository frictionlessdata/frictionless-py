from __future__ import annotations
from ...plugin import Plugin
from .control import ParquetControl
from .parser import ParquetParser


class ParquetPlugin(Plugin):
    """Plugin for Parquet"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "parquet":
            return ParquetControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "parq":
            return ParquetParser(resource)

    def detect_resource(self, resource):
        if resource.format == "parq":
            resource.type = "table"
            resource.mediatype = "appliction/parquet"
