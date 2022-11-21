from __future__ import annotations
import attrs
from typing import Optional
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_subset(Step):
    """Subset rows.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "row-subset"

    # State

    subset: str
    """
    It can take different values such as "conflicts","distinct","duplicates"
    and "unique".
    """

    field_name: Optional[str] = None
    """
    Name of field to which the subset functions will be applied. 
    """

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if self.subset == "conflicts":
            resource.data = table.conflicts(self.field_name)  # type: ignore
        elif self.subset == "distinct":
            resource.data = table.distinct(self.field_name)  # type: ignore
        elif self.subset == "duplicates":
            resource.data = table.duplicates(self.field_name)  # type: ignore
        elif self.subset == "unique":
            resource.data = table.unique(self.field_name)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "type": "object",
        "required": ["subset"],
        "properties": {
            "subset": {
                "type": "string",
                "enum": ["conflicts", "distinct", "duplicates", "unique"],
            },
            "fieldName": {"type": "string"},
        },
    }
