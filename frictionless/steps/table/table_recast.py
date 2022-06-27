from typing import List
from dataclasses import dataclass, field
from ...pipeline import Step


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


@dataclass
class table_recast(Step):
    """Recast table"""

    code = "table-recast"

    # Properties

    field_name: str
    """TODO: add docs"""

    from_field_names: List[str] = field(default_factory=lambda: ["variable", "value"])
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.pop("schema", None)
        resource.data = table.recast(  # type: ignore
            key=self.field_name,
            variablefield=self.from_field_names[0],
            valuefield=self.from_field_names[1],
        )
        resource.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldName"],
        "properties": {
            "code": {},
            "fieldName": {"type": "string"},
            "fromFieldNames": {"type": "array", "minItems": 2, "maxItems": 2},
        },
    }
