from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class cell_format(Step):
    """Format cell

    Formats all values in the given or all string fields using the `template` format string.

    """

    type = "cell-format"

    template: str
    """format string to apply to cells"""

    field_name: Optional[str] = None
    """field name to apply template format"""

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        if not self.field_name:
            resource.data = table.formatall(self.template)  # type: ignore
        else:
            resource.data = table.format(self.field_name, self.template)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
