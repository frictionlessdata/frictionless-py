from __future__ import annotations
from ...system import Plugin
from ...records import PathDetails
from .control import ParquetControl
from .parser import ParquetParser


class ParquetPlugin(Plugin):
    """Plugin for Parquet"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "parq" or resource.format == "parquet":
            return ParquetParser(resource)

    def detect_path_details(self, details: PathDetails):
        if details.format == "parq" or details.format == "parquet":
            details.type = "table"
            details.mediatype = "appliction/parquet"

    def select_Control(self, type):
        if type == "parquet":
            return ParquetControl
