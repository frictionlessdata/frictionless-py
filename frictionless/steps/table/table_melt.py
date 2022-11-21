from __future__ import annotations
import attrs
from typing import Optional, List
from ...pipeline import Step
from ... import fields


@attrs.define(kw_only=True)
class table_melt(Step):
    """Melt tables.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-melt"

    # State

    field_name: str
    """
    Field name which will be use to melt table. It will keep
    the field 'field_name' as it is but melt other fields into
    data.
    """

    variables: Optional[str] = None
    """
    List of name of fields which will be melted into data.
    """

    to_field_names: List[str] = attrs.field(factory=lambda: ["variable", "value"])
    """
    Labels for new fields that will be created "variable" and "value".
    """

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field = resource.schema.get_field(self.field_name)
        resource.schema.fields.clear()
        resource.schema.add_field(field)
        resource.schema.add_field(fields.StringField(name=self.to_field_names[0]))
        resource.schema.add_field(fields.AnyField(name=self.to_field_names[1]))
        resource.data = table.melt(  # type: ignore
            key=self.field_name,
            variables=self.variables,
            variablefield=self.to_field_names[0],
            valuefield=self.to_field_names[1],
        )

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldName"],
        "properties": {
            "fieldName": {"type": "string"},
            "variables": {"type": "array"},
            "toFieldNames": {"type": "array", "minItems": 2, "maxItems": 2},
        },
    }
