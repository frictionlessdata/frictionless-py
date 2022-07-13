from __future__ import annotations
import attrs
import petl
from typing import Optional
from ...pipeline import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


@attrs.define(kw_only=True)
class cell_replace(Step):
    """Replace cell"""

    type = "cell-replace"

    # State

    pattern: str
    """TODO: add docs"""

    replace: str
    """TODO: add docs"""

    field_name: Optional[str] = None
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if not self.field_name:
            resource.data = table.replaceall(self.pattern, self.replace)  # type: ignore
        else:
            pattern = self.pattern
            function = petl.replace
            if pattern.startswith("<regex>"):  # type: ignore
                pattern = pattern.replace("<regex>", "")  # type: ignore
                function = petl.sub
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
