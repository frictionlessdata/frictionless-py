from __future__ import annotations
import attrs
from typing import Optional
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_subset(Step):
    """Subset rows"""

    type = "row-subset"

    # State

    subset: str
    """NOTE: add docs"""

    field_name: Optional[str] = None
    """NOTE: add docs"""

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
