# type: ignore
from __future__ import annotations
import attrs
from ...pipeline import Step


@attrs.define(kw_only=True)
class field_move(Step):
    """Move field.

    This step can be added using the `steps` parameter
    for the `transform` function.
    """

    type = "field-move"

    # State

    name: str
    """
    Field name to move.
    """

    position: int
    """
    New position for the field being moved.
    """

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
