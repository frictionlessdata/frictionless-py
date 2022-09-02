from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_sort(Step):
    """Sort rows"""

    type = "row-sort"

    # State

    field_names: List[str]
    """NOTE: add docs"""

    reverse: bool = False
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.data = table.sort(self.field_names, reverse=self.reverse)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldNames"],
        "properties": {
            "fieldNames": {"type": "array"},
            "reverse": {},
        },
    }
