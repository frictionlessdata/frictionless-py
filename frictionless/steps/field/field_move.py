from dataclasses import dataclass
from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


@dataclass
class field_move(Step):
    """Move field"""

    code = "field-move"

    # Properties

    name: str
    """TODO: add docs"""

    position: int
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field = resource.schema.remove_field(self.name)
        resource.schema.fields.insert(self.position - 1, field)  # type: ignore
        resource.data = table.movefield(self.name, self.position - 1)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "position"],
        "properties": {
            "code": {},
            "name": {"type": "string"},
            "position": {"type": "number"},
        },
    }
