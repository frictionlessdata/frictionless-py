from ...plugin import Plugin
from .dialect import PandasDialect
from .parser import PandasParser
from ... import helpers


# NOTE:
# We need to ensure that the way we detect pandas dataframe is good enough.
# We don't want to be importing pandas and checking the type without a good reason


class PandasPlugin(Plugin):
    """Plugin for Pandas

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.pandas import PandasPlugin`

    """

    code = "pandas"
    status = "experimental"

    def create_file(self, file):
        if not file.scheme and not file.format and file.memory:
            if helpers.is_type(file.data, "DataFrame"):
                file.scheme = ""
                file.format = "pandas"
                return file

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "pandas":
            return PandasDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "pandas":
            return PandasParser(resource)
