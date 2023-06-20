from __future__ import annotations

from typing import TYPE_CHECKING, List

import attrs

from ... import fields
from ...pipeline import Step
from ...platform import platform

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class field_split(Step):
    """Split field.

    This step can be added using the `steps` parameter
    for the `transform` function.
    """

    type = "field-split"

    name: str
    """
    Name of the field to split.
    """

    to_names: List[str]
    """
    List of names of new fields.
    """

    pattern: str
    """
    Pattern to split the field value, for example: "a".
    """

    preserve: bool = False
    """
    Whether to preserve the fields after the split. If True,
    the fields are not removed after split.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        for to_name in self.to_names:
            field = fields.StringField(name=to_name)
            resource.schema.add_field(field)
        if not self.preserve:
            resource.schema.remove_field(self.name)
        processor = platform.petl.split  # type: ignore
        # NOTE: this condition needs to be improved
        if "(" in self.pattern:
            processor = platform.petl.capture  # type: ignore
        resource.data = processor(  # type: ignore
            table,  # type: ignore
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
