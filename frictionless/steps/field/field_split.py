from __future__ import annotations
import attrs
from typing import List
from ...platform import platform
from ...pipeline import Step
from ... import fields


@attrs.define(kw_only=True)
class field_split(Step):
    """Split field"""

    type = "field-split"

    # State

    name: str
    """NOTE: add docs"""

    to_names: List[str]
    """NOTE: add docs"""

    pattern: str
    """NOTE: add docs"""

    preserve: bool = False
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        for to_name in self.to_names:
            field = fields.StringField(name=to_name)
            resource.schema.add_field(field)
        if not self.preserve:
            resource.schema.remove_field(self.name)
        processor = platform.petl.split
        # NOTE: this condition needs to be improved
        if "(" in self.pattern:
            processor = platform.petl.capture
        resource.data = processor(
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
            "toNames": {"type": "array"},
            "pattern": {"type": "string"},
            "preserve": {"type": "boolean"},
        },
    }
