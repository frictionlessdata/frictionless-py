from ...step import Step
from ...field import Field


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


class field_unpack(Step):
    """Unpack field"""

    code = "field-unpack"

    def __init__(self, descriptor=None, *, name=None, to_names=None, preserve=False):
        self.setinitial("name", name)
        self.setinitial("toNames", to_names)
        self.setinitial("preserve", preserve)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        name = self.get("name")
        to_names = self.get("toNames")
        preserve = self.get("preserve")
        field = resource.schema.get_field(name)
        for to_name in to_names:
            resource.schema.add_field(Field(name=to_name))
        if not preserve:
            resource.schema.remove_field(name)
        if field.type == "object":
            processor = table.unpackdict
            resource.data = processor(name, to_names, includeoriginal=preserve)
        else:
            processor = table.unpack
            resource.data = processor(name, to_names, include_original=preserve)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "toNames"],
        "properties": {
            "name": {"type": "string"},
            "toNames": {"type": "array"},
            "preserve": {},
        },
    }
