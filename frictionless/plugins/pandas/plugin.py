from ...plugin import Plugin
from .control import PandasControl
from .parser import PandasParser
from ... import helpers


# NOTE:
# We need to ensure that the way we detect pandas dataframe is good enough.
# We don't want to be importing pandas and checking the type without a good reason


class PandasPlugin(Plugin):
    """Plugin for Pandas"""

    code = "pandas"
    status = "experimental"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "pandas":
            return PandasControl.from_descriptor(descriptor)

    def create_file(self, file):
        if not file.scheme and not file.format and file.memory:
            if helpers.is_type(file.data, "DataFrame"):
                file.scheme = ""
                file.format = "pandas"
                return file

    def create_parser(self, resource):
        if resource.format == "pandas":
            return PandasParser(resource)
