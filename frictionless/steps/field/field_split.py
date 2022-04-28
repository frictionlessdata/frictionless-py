import petl
from ...step import Step
from ...field import Field


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


class field_split(Step):
    """Split field"""

    code = "field-split"

    def __init__(
        self,
        descriptor=None,
        *,
        name=None,
        to_names=None,
        pattern=None,
        preserve=False,
    ):
        self.setinitial("name", name)
        self.setinitial("toNames", to_names)
        self.setinitial("pattern", pattern)
        self.setinitial("preserve", preserve)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        name = self.get("name")
        to_names = self.get("toNames")
        pattern = self.get("pattern")
        preserve = self.get("preserve")
        for to_name in to_names:
            resource.schema.add_field(Field(name=to_name, type="string"))
        if not preserve:
            resource.schema.remove_field(name)
        processor = petl.split
        # NOTE: this condition needs to be improved
        if "(" in pattern:
            processor = petl.capture
        resource.data = processor(
            table,
            name,
            pattern,
            to_names,
            include_original=preserve,
        )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "toNames", "pattern"],
        "properties": {
            "name": {"type": "string"},
            "toNames": {},
            "pattern": {},
            "preserve": {},
        },
    }
