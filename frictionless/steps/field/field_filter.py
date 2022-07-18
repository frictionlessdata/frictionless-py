from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


class field_filter(Step):
    """Filter fields"""

    code = "field-filter"

    def __init__(self, descriptor=None, *, names=None):
        self.setinitial("names", names)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        names = self.get("names", [])
        schema_fields_dict = {dct["name"]: dct for dct in resource.schema.fields}
        new_schema_fields = [
            schema_fields_dict[name] for name in names if name in schema_fields_dict
        ]
        resource.schema.fields = new_schema_fields
        new_names = [dct["name"] for dct in new_schema_fields]
        resource.data = table.cut(*new_names)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["names"],
        "properties": {
            "names": {"type": "array"},
        },
    }
