from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Step


@attrs.define(kw_only=True)
class field_filter(Step):
    """Filter fields.

    This step can be added using the `steps` parameter
    for the `transform` function.
    """

    type = "field-filter"

    # State

    names: List[str]
    """
    Names of the field to be read. Other fields will be ignored.
    """

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        for name in resource.schema.field_names:
            if name not in self.names:
                resource.schema.remove_field(name)
        resource.data = table.cut(*resource.schema.field_names)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "type": "object",
        "required": ["names"],
        "properties": {
            "names": {"type": "array"},
        },
    }
