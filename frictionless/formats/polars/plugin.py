from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ... import helpers
from ...platform import platform
from ...system import Plugin
from .control import PolarsControl
from .parser import PolarsParser

if TYPE_CHECKING:
    from ...resource import Resource


# NOTE:
# We need to ensure that the way we detect pandas dataframe is good enough.
# We don't want to be importing pandas and checking the type without a good reason


class PolarsPlugin(Plugin):
    """Plugin for Polars"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format == "polars":
            return PolarsParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.data is not None:
            if helpers.is_type(resource.data, "polars.dataframe.frame.DataFrame"):
                resource.format = resource.format or "polars"
        if resource.format == "polars":
            if resource.data is None:
                resource.data = platform.polars.DataFrame()
            resource.datatype = resource.datatype or "table"
            resource.mediatype = resource.mediatype or "application/polars"

    def select_control_class(self, type: Optional[str] = None):
        if type == "polars":
            return PolarsControl
