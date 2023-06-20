from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ...system import Plugin
from .control import SpssControl
from .parser import SpssParser

if TYPE_CHECKING:
    from ...resource import Resource


class SpssPlugin(Plugin):
    """Plugin for SPSS"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format in ["sav", "zsav"]:
            return SpssParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format in ["sav", "zsav"]:
            resource.datatype = resource.datatype or "table"

    def select_control_class(self, type: Optional[str] = None):
        if type == "spss":
            return SpssControl
