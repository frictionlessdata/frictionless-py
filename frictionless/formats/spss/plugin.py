from __future__ import annotations
from ...system import Plugin
from .control import SpssControl
from .parser import SpssParser


class SpssPlugin(Plugin):
    """Plugin for SPSS"""

    # Hooks

    def create_parser(self, resource):
        if resource.format in ["sav", "zsav"]:
            return SpssParser(resource)

    def detect_resource(self, resource):
        if resource.format in ["sav", "zsav"]:
            resource.type = "table"

    def select_Control(self, type):
        if type == "spss":
            return SpssControl
