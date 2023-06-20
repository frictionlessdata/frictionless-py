from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class row_split(Step):
    """Split rows.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "row-add"

    pattern: str
    """
    Pattern to search for in one or more fields.
    """

    field_name: str
    """
    Field name whose cell value will be splitted.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        resource.data = table.splitdown(self.field_name, self.pattern)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldName", "pattern"],
        "properties": {
            "fieldName": {"type": "string"},
            "pattern": {"type": "string"},
        },
    }
