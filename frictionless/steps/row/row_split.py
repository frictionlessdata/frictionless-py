from __future__ import annotations
import attrs
from ...pipeline import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


@attrs.define(kw_only=True)
class row_split(Step):
    """Split rows"""

    type = "row-add"

    # State

    pattern: str
    """TODO: add docs"""

    field_name: str
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.data = table.splitdown(self.field_name, self.pattern)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldName", "pattern"],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "fieldName": {"type": "string"},
            "pattern": {"type": "string"},
        },
    }
