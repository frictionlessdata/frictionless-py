from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_fill(Step):
    """Fill cell"""

    code = "cell-fill"

    def __init__(self, descriptor=None, *, value=None, field_name=None, direction=None):
        self.setinitial("value", value)
        self.setinitial("fieldName", field_name)
        self.setinitial("direction", direction)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        value = self.get("value")
        field_name = self.get("fieldName")
        direction = self.get("direction")
        if value:
            resource.data = table.convert(field_name, {None: value})
        elif direction == "down":
            if field_name:
                resource.data = table.filldown(field_name)
            else:
                resource.data = table.filldown()
        elif direction == "right":
            resource.data = table.fillright()
        elif direction == "left":
            resource.data = table.fillleft()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "fieldName": {"type": "string"},
            "value": {},
            "direction": {
                "type": "string",
                "enum": ["down", "right", "left"],
            },
        },
    }
