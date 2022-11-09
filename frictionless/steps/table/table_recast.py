from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Step


@attrs.define(kw_only=True)
class table_recast(Step):
    """Recast table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-recast"

    # State

    field_name: str
    """
    Recast table by the field 'field_name'.
    """

    from_field_names: List[str] = attrs.field(factory=lambda: ["variable", "value"])
    """
    List of field names for the output table.
    """

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
