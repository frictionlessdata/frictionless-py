from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_interpolate(Step):
    """Interpolate cell"""

    code = "cell-interpolate"

    def __init__(self, descriptor=None, *, template=None, field_name=None):
        self.setinitial("template", template)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        template = self.get("template")
        field_name = self.get("fieldName")
        table = resource.to_petl()
        if not field_name:
            resource.data = table.interpolateall(template)
        else:
            resource.data = table.interpolate(field_name, template)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
