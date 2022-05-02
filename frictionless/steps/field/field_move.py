from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


class field_move(Step):
    """Move field"""

    code = "field-move"

    def __init__(self, descriptor=None, *, name=None, position=None):
        self.setinitial("name", name)
        self.setinitial("position", position)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        name = self.get("name")
        position = self.get("position")
        field = resource.schema.remove_field(name)
        resource.schema.fields.insert(position - 1, field)
        resource.data = table.movefield(name, position - 1)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "position"],
        "properties": {
            "name": {"type": "string"},
            "position": {"type": "number"},
        },
    }
