# type: ignore
from __future__ import annotations

from typing import List

import attrs

from ...pipeline import Step


@attrs.define(kw_only=True, repr=False)
class field_remove(Step):
    """Remove field.

    This step can be added using the `steps` parameter
    for the `transform` function.
    """

    type = "field-remove"

    names: List[str]
    """
    List of fields to remove.
    """

    # Transform

    def transform_resource(self, resource):
        indexes = []
        table = resource.to_petl()
        for index, field in list(enumerate(resource.schema.fields)):
            if field.name in self.names:
                resource.schema.remove_field(field.name)
                indexes.append(index)
        resource.data = table.cutout(*indexes)

    # Metadata

    metadata_profile_patch = {
        "required": ["names"],
        "properties": {
            "names": {"type": "array"},
        },
    }
