from typing import Optional, Any
from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_fill(Step):
    """Fill cell"""

    code = "cell-fill"

    def __init__(
        self,
        *,
        value: Optional[Any] = None,
        field_name: Optional[str] = None,
        direction: Optional[str] = None,
    ):
        self.value = value
        self.field_name = field_name
        self.direction = direction

    # Properties

    value: Optional[Any]
    """TODO: add docs"""

    field_name: Optional[str]
    """TODO: add docs"""

    direction: Optional[str]
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if self.value:
            resource.data = table.convert(field_name, {None: value})  # type: ignore
        elif self.direction == "down":
            if self.field_name:
                resource.data = table.filldown(self.field_name)  # type: ignore
            else:
                resource.data = table.filldown()  # type: ignore
        elif self.direction == "right":
            resource.data = table.fillright()  # type: ignore
        elif self.direction == "left":
            resource.data = table.fillleft()  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "code": {},
            "fieldName": {"type": "string"},
            "value": {},
            "direction": {
                "type": "string",
                "enum": ["down", "right", "left"],
            },
        },
    }
