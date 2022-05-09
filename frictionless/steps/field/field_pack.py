from ...step import Step
from ...field import Field
from ...helpers import iterpack, iterpackdict


class field_pack(Step):
    """Pack field"""

    code = "field-pack"

    def __init__(
        self,
        descriptor=None,
        *,
        name=None,
        from_names=None,
        field_type=None,
        preserve=False
    ):
        self.setinitial("name", name)
        self.setinitial("fromNames", from_names)
        self.setinitial("fieldType", field_type)
        self.setinitial("preserve", preserve)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        name = self.get("name")
        from_names = self.get("fromNames")
        field_type = self.get("fieldType")
        preserve = self.get("preserve")
        resource.schema.add_field(Field(name=name))
        if not preserve:
            for name in from_names:
                resource.schema.remove_field(name)
        if field_type == "object":
            resource.data = iterpackdict(
                table, "detail", ["name", "population"], preserve
            )
        else:
            resource.data = iterpack(table, "detail", ["name", "population"], preserve)

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["name", "fromNames"],
        "properties": {
            "name": {"type": "string"},
            "fromNames": {"type": "array"},
            "fieldType": {"type": "string"},
            "preserve": {},
        },
    }
