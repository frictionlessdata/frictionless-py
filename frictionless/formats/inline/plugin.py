from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Any, Optional

from ...detector import Detector
from ...system import Plugin
from .control import InlineControl
from .parser import InlineParser

if TYPE_CHECKING:
    from ...resource import Resource


class InlinePlugin(Plugin):
    """Plugin for Inline"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format == "inline":
            return InlineParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.data is not None:
            if not hasattr(resource.data, "read"):
                types: Any = (list, typing.Iterator, typing.Generator)
                if callable(resource.data) or isinstance(resource.data, types):
                    resource.format = resource.format or "inline"
                    resource.datatype = resource.datatype or "table"
                elif isinstance(resource.data, dict):
                    resource.format = resource.format or "inline"
                    resource.datatype = (
                        resource.datatype
                        or Detector.detect_metadata_type(resource.data)
                        or "json"
                    )
        # TODO: remove
        elif resource.format == "inline":
            resource.data = []

    def select_control_class(self, type: Optional[str] = None):
        if type == "inline":
            return InlineControl
