from __future__ import annotations
import attrs
from typing import Optional
from ...platform import platform
from ...pipeline import Step


@attrs.define(kw_only=True)
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

    def transform_resource(self, resource):
        table = resource.to_petl()  # type: ignore
        if not self.field_name:
            resource.data = table.replaceall(self.pattern, self.replace)  # type: ignore
        else:
            pattern = self.pattern
            function = platform.petl.replace
            if pattern.startswith("<regex>"):  # type: ignore
                pattern = pattern.replace("<regex>", "")  # type: ignore
                function = platform.petl.sub
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
