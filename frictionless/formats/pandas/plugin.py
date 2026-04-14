from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ... import helpers
from ...platform import platform
from ...system import Plugin
from .control import PandasControl
from .parser import PandasParser

if TYPE_CHECKING:
    from ...resource import Resource


# NOTE:
# We need to ensure that the way we detect pandas dataframe is good enough.
# We don't want to be importing pandas and checking the type without a good reason


class PandasPlugin(Plugin):
    """Plugin for Pandas"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format == "pandas":
            return PandasParser(resource)

    def matches_datatype(self, resource: Resource):
        if resource.data is not None and helpers.is_type(resource.data, "DataFrame"):
            return "table"
        if resource.format == "pandas":
            return "table"

    def detect_resource(self, resource: Resource):
        is_dataframe = resource.data is not None and helpers.is_type(
            resource.data, "DataFrame"
        )
        if is_dataframe or resource.format == "pandas":
            resource.format = resource.format or "pandas"
            if resource.data is None:
                resource.data = platform.pandas.DataFrame()
            resource.mediatype = resource.mediatype or "application/pandas"

    def select_control_class(self, type: Optional[str] = None):
        if type == "pandas":
            return PandasControl
