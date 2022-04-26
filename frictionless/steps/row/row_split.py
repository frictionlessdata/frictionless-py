from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_split(Step):
    """Split rows"""

    code = "row-add"

    def __init__(self, descriptor=None, *, pattern=None, field_name=None):
        self.setinitial("pattern", pattern)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        pattern = self.get("pattern")
        field_name = self.get("fieldName")
        resource.data = table.splitdown(field_name, pattern)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldName", "pattern"],
        "properties": {
            "fieldName": {"type": "string"},
            "pattern": {"type": "string"},
        },
    }
