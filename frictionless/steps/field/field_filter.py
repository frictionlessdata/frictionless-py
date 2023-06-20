from __future__ import annotations

from typing import TYPE_CHECKING, List

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class field_filter(Step):
    """Filter fields.

    This step can be added using the `steps` parameter
    for the `transform` function.
    """

    type = "field-filter"

    names: List[str]
    """
    Names of the field to be read. Other fields will be ignored.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
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
