# type: ignore
from __future__ import annotations

from typing import List

import attrs

from ... import fields
from ...pipeline import Step


@attrs.define(kw_only=True, repr=False)
class field_unpack(Step):
    """Unpack field.

    This step can be added using the `steps` parameter for the
    `transform` function.

    """

    type = "field-unpack"

    name: str
    """
    Name of the field to unpack.
    """

    to_names: List[str]
    """
    List of names for new fields that will be created
    after unpacking.
    """

    preserve: bool = False
    """
    Whether to preserve the source fields after unpacking.
    """

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field = resource.schema.get_field(self.name)
        for to_name in self.to_names:
            resource.schema.add_field(fields.AnyField(name=to_name))
        if not self.preserve:
            resource.schema.remove_field(self.name)
        processor = table.unpack
        options = dict(include_original=self.preserve)
        if field.type == "object":
            processor = table.unpackdict
            options = dict(includeoriginal=self.preserve)
        resource.data = processor(self.name, self.to_names, **options)

    # Metadata

    metadata_profile_patch = {
        "required": ["name", "toNames"],
        "properties": {
            "name": {"type": "string"},
            "toNames": {"type": "array"},
            "preserve": {},
        },
    }
