from __future__ import annotations
import attrs
import petl
from typing import Optional
from ...pipeline import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


@attrs.define(kw_only=True)
class row_search(Step):
    """Search rows"""

    type = "row-search"

    # State

    regex: str
    """TODO: add docs"""

    field_name: Optional[str] = None
    """TODO: add docs"""

    negate: bool = False
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        search = petl.searchcomplement if self.negate else petl.search
        if self.field_name:
            resource.data = search(table, self.field_name, self.regex)  # type: ignore
        else:
            resource.data = search(table, self.regex)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["regex"],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "regex": {},
            "fieldName": {"type": "string"},
            "negate": {},
        },
    }
