from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Step


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


@attrs.define(kw_only=True)
class table_recast(Step):
    """Recast table"""

    type = "table-recast"

    # State

    field_name: str
    """NOTE: add docs"""

    from_field_names: List[str] = attrs.field(factory=lambda: ["variable", "value"])
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.schema = None
        resource.data = table.recast(  # type: ignore
            key=self.field_name,
            variablefield=self.from_field_names[0],
            valuefield=self.from_field_names[1],
        )
        resource.infer()

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldName"],
        "properties": {
            "fieldName": {"type": "string"},
            "fromFieldNames": {"type": "array", "minItems": 2, "maxItems": 2},
        },
    }
