from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_subset(Step):
    """Subset rows"""

    code = "row-subset"

    def __init__(self, descriptor=None, *, subset=None, field_name=None):
        self.setinitial("subset", subset)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        subset = self.get("subset")
        field_name = self.get("fieldName")
        if subset == "conflicts":
            resource.data = table.conflicts(field_name)
        elif subset == "distinct":
            resource.data = table.distinct(field_name)
        elif subset == "duplicates":
            resource.data = table.duplicates(field_name)
        elif subset == "unique":
            resource.data = table.unique(field_name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["subset"],
        "properties": {
            "subset": {
                "type": "string",
                "enum": ["conflicts", "distinct", "duplicates", "unique"],
            },
            "fieldName": {"type": "string"},
        },
    }
