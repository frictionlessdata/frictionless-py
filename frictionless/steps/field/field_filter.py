# type: ignore
from typing import List
from dataclasses import dataclass
from ...pipeline import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


@dataclass
class field_filter(Step):
    """Filter fields"""

    type = "field-filter"

    # Properties

    names: List[str]
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        for name in resource.schema.field_names:
            if name not in self.names:
                resource.schema.remove_field(name)
        resource.data = table.cut(*self.names)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["names"],
        "properties": {
            "type": {},
            "names": {"type": "array"},
        },
    }
