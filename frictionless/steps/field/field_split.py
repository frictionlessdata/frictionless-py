# type: ignore
from __future__ import annotations
import attrs
from typing import Optional, List
from ...platform import platform
from ...pipeline import Step
from ...schema import Field


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


@attrs.define(kw_only=True)
class field_split(Step):
    """Split field"""

    type = "field-split"

    # State

    name: str
    """NOTE: add docs"""

    to_names: List[str]
    """NOTE: add docs"""

    pattern: Optional[str] = None
    """NOTE: add docs"""

    preserve: bool = False
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        for to_name in self.to_names:  # type: ignore
            resource.schema.add_field(Field(name=to_name, type="string"))
        if not self.preserve:
            resource.schema.remove_field(self.name)
        processor = platform.petl.split
        # NOTE: this condition needs to be improved
        if "(" in self.pattern:  # type: ignore
            processor = platform.petl.capture
        resource.data = processor(  # type: ignore
            table,
            self.name,
            self.pattern,
            self.to_names,
            include_original=self.preserve,  # type: ignore
        )

    # Metadata

    metadata_profile_patch = {
        "required": ["name", "toNames", "pattern"],
        "properties": {
            "name": {"type": "string"},
            "toNames": {},
            "pattern": {},
            "preserve": {},
        },
    }
