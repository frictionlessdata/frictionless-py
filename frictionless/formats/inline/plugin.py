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
    """Handles data already parsed to python object, provided through the
    resource "data" property
    """

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format == "inline":
            return InlineParser(resource)

    def matches_datatype(self, resource: Resource):
        if resource.data is not None:
            if hasattr(resource.data, "read"):
                # raw-bytes - handled by the StreamPlugin
                return None

            if isinstance(resource.data, dict):
                return Detector.detect_metadata_type(resource.data) or "json"  # pyright: ignore[reportUnknownMemberType]

            is_iterable = isinstance(
                resource.data, (list, typing.Iterator, typing.Generator)
            )
            is_factory = callable(resource.data)
            if is_factory or is_iterable:
                return "table"

        # Degenerate case: format=inline, no data. `detect_resource` will seed
        # table data
        if resource.data is None and resource.format == "inline":
            return resource.datatype or "table"

    def detect_resource(self, resource: Resource):
        # Mirrors matches_datatype: inline owns resources with in-memory data
        # (dict/iterable/callable) or explicit format=inline.
        if resource.data is not None and not hasattr(resource.data, "read"):
            is_inline = isinstance(
                resource.data,
                (dict, list, typing.Iterator, typing.Generator),
            ) or callable(resource.data)
            if is_inline:
                resource.format = resource.format or "inline"
        elif resource.data is None and resource.format == "inline":
            resource.data = []

    def select_control_class(self, type: Optional[str] = None):
        if type == "inline":
            return InlineControl
