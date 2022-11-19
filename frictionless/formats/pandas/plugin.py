from __future__ import annotations
from ...system import Plugin
from .control import PandasControl
from .parser import PandasParser
from ...platform import platform
from ... import helpers


# NOTE:
# We need to ensure that the way we detect pandas dataframe is good enough.
# We don't want to be importing pandas and checking the type without a good reason


class PandasPlugin(Plugin):
    """Plugin for Pandas"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "pandas":
            return PandasParser(resource)

    def detect_resource(self, resource):
        if resource.data is not None:
            if helpers.is_type(resource.data, "DataFrame"):
                resource.type = "table"
                resource.scheme = ""
                resource.format = "pandas"
                resource.mediatype = "application/pandas"
        elif resource.format == "pandas":
            resource.data = platform.pandas.DataFrame()

    def select_Control(self, type):
        if type == "pandas":
            return PandasControl
