from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_convert(Step):
    """Convert cell"""

    code = "cell-convert"

    def __init__(self, descriptor=None, *, value=None, function=None, field_name=None):
        self.setinitial("value", value)
        self.setinitial("function", function)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field_name = self.get("fieldName")
        function = self.get("function")
        value = self.get("value")
        if not field_name:
            if not function:
                function = lambda input: value
            resource.data = table.convertall(function)
        elif function:
            resource.data = table.convert(field_name, function)
        else:
            resource.data = table.update(field_name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "value": {},
            "fieldName": {"type": "string"},
        },
    }
