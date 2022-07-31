# type: ignore
from __future__ import annotations
import attrs
from ...pipeline import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


@attrs.define(kw_only=True)
class field_move(Step):
    """Move field"""

    type = "field-move"

    # State

    name: str
    """NOTE: add docs"""

    position: int
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field = resource.schema.remove_field(self.name)
        resource.schema.fields.insert(self.position - 1, field)  # type: ignore
        resource.data = table.movefield(self.name, self.position - 1)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["name", "position"],
        "properties": {
            "name": {"type": "string"},
            "position": {"type": "number"},
        },
    }
