# type: ignore
from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Step


@attrs.define(kw_only=True)
class field_remove(Step):
    """Remove field.

    This step can be added using the `steps` parameter
    for the `transform` function.
    """

    type = "field-remove"

    # State

    names: List[str]
    """
    List of fields to remove.
    """

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        for name in self.names:  # type: ignore
            resource.schema.remove_field(name)
        resource.data = table.cutout(*self.names)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["names"],
        "properties": {
            "names": {"type": "array"},
        },
    }
