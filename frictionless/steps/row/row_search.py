from __future__ import annotations
import attrs
from typing import Optional
from ...platform import platform
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_search(Step):
    """Search rows"""

    type = "row-search"

    # State

    regex: str
    """NOTE: add docs"""

    field_name: Optional[str] = None
    """NOTE: add docs"""

    negate: bool = False
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        search = platform.petl.searchcomplement if self.negate else platform.petl.search
        if self.field_name:
            resource.data = search(table, self.field_name, self.regex)  # type: ignore
        else:
            resource.data = search(table, self.regex)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["regex"],
        "properties": {
            "regex": {},
            "fieldName": {"type": "string"},
            "negate": {},
        },
    }
