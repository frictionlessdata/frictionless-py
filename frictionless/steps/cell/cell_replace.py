from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import attrs

from ...pipeline import Step
from ...platform import platform

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class cell_replace(Step):
    """Replace cell

    Replace cell values in a given field or all fields using user defined pattern.
    """

    type = "cell-replace"

    pattern: str
    """Pattern to search for in single or all fields"""

    replace: str
    """String to replace"""

    field_name: Optional[str] = None
    """field name to apply template string"""

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        if not self.field_name:
            resource.data = table.replaceall(self.pattern, self.replace)  # type: ignore
        else:
            pattern = self.pattern
            function = platform.petl.replace  # type: ignore
            if pattern.startswith("<regex>"):  # type: ignore
                pattern = pattern.replace("<regex>", "")  # type: ignore
                function = platform.petl.sub  # type: ignore
            resource.data = function(table, self.field_name, pattern, self.replace)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["pattern"],
        "properties": {
            "pattern": {"type": "string"},
            "replace": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
