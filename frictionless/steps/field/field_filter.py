from typing import List
from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


class field_filter(Step):
    """Filter fields"""

    code = "field-filter"

    def __init__(
        self,
        *,
        names: List[str],
    ):
        self.names = names

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
            "code": {},
            "names": {"type": "array"},
        },
    }
