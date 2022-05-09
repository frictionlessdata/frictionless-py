from ...step import Step
from ...field import Field
from ...helpers import merge
from typing import List


class field_merge(Step):
    """Merge field"""

    code = "field-merge"

    def __init__(
        self,
        descriptor: any = None,
        *,
        name: str = None,
        from_names: List[str] = None,
        separator: str = "-",
        preserve: bool = False
    ):
        self.setinitial("name", name)
        self.setinitial("fromNames", from_names)
        self.setinitial("separator", separator)
        self.setinitial("preserve", preserve)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource: any) -> None:
        table = resource.to_petl()
        name = self.get("name")
        from_names = self.get("fromNames")
        separator = self.get("separator")
        preserve = self.get("preserve")
        resource.schema.add_field(Field(name=name))
        if not preserve:
            for name in from_names:
                resource.schema.remove_field(name)
        resource.data = merge(table, name, from_names, separator, preserve)

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["name", "fromNames"],
        "properties": {
            "name": {"type": "string"},
            "fromNames": {"type": "array"},
            "preserve": {},
        },
    }
