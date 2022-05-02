from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_sort(Step):
    """Sort rows"""

    code = "row-sort"

    def __init__(self, descriptor=None, *, field_names=None, reverse=None):
        self.setinitial("fieldNames", field_names)
        self.setinitial("reverse", reverse)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field_names = self.get("fieldNames")
        reverse = self.get("reverse", False)
        resource.data = table.sort(field_names, reverse=reverse)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldNames"],
        "properties": {
            "fieldNames": {"type": "array"},
            "reverse": {},
        },
    }
