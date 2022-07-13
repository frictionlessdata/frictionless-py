# type: ignore
from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


@attrs.define(kw_only=True)
class field_remove(Step):
    """Remove field"""

    type = "field-remove"

    # State

    names: List[str]
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        for name in self.names:  # type: ignore
            resource.schema.remove_field(name)
        resource.data = table.cutout(*self.names)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["names"],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "names": {"type": "array"},
        },
    }
