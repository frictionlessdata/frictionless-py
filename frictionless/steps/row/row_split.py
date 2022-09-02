from __future__ import annotations
import attrs
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_split(Step):
    """Split rows"""

    type = "row-add"

    # State

    pattern: str
    """NOTE: add docs"""

    field_name: str
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.data = table.splitdown(self.field_name, self.pattern)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldName", "pattern"],
        "properties": {
            "fieldName": {"type": "string"},
            "pattern": {"type": "string"},
        },
    }
