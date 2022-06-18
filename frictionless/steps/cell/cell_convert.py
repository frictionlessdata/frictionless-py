from typing import Optional, Any
from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_convert(Step):
    """Convert cell"""

    code = "cell-convert"

    def __init__(
        self,
        *,
        value: Optional[Any] = None,
        function: Optional[Any] = None,
        field_name: Optional[str] = None,
    ):
        self.value = value
        self.function = function
        self.field_name = field_name

    # Properties

    value: Optional[Any]
    """TODO: add docs"""

    function: Optional[Any]
    """TODO: add docs"""

    field_name: Optional[str]
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        function = self.function
        if not self.field_name:
            if not function:
                function = lambda _: self.value
            resource.data = table.convertall(function)  # type: ignore
        elif self.function:
            resource.data = table.convert(self.field_name, function)  # type: ignore
        else:
            resource.data = table.update(self.field_name, self.value)  # type: ignore

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": [],
        "properties": {
            "code": {},
            "value": {},
            "fieldName": {"type": "string"},
        },
    }
