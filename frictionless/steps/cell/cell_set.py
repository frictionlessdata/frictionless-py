from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_set(Step):
    """Set cell"""

    code = "cell-set"

    def __init__(self, descriptor=None, *, value=None, field_name=None):
        self.setinitial("value", value)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    def transform_resource(self, resource):
        table = resource.to_petl()
        value = self.get("value")
        field_name = self.get("fieldName")
        resource.data = table.update(field_name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "fieldName": {"type": "string"},
            "value": {},
        },
    }
