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
        names = self.get("names")
        for name in resource.schema.field_names:
            if name not in names:
                resource.schema.remove_field(name)
        resource.data = table.cut(*names)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["names"],
        "properties": {
            "names": {"type": "array"},
        },
    }
