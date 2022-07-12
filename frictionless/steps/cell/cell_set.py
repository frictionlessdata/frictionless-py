from typing import Any
from dataclasses import dataclass
from ...pipeline import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


@dataclass
class cell_set(Step):
    """Set cell"""

    type = "cell-set"

    # Properties

    value: Any
    """TODO: add docs"""

    field_name: str
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.data = table.update(self.field_name, self.value)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "type": {},
            "fieldName": {"type": "string"},
            "value": {},
        },
    }
