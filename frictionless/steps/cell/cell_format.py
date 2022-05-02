from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_format(Step):
    """Format cell"""

    code = "cell-format"

    def __init__(self, descriptor=None, *, template=None, field_name=None):
        self.setinitial("template", template)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field_name = self.get("fieldName")
        template = self.get("template")
        if not field_name:
            resource.data = table.formatall(template)
        else:
            resource.data = table.format(field_name, template)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
