import petl
from dataclasses import dataclass
from typing import Optional, List
from ...step import Step
from ...schema import Field


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


@dataclass
class field_split(Step):
    """Split field"""

    code = "field-split"

    # Properties

    name: str
    """TODO: add docs"""

    to_names: List[str]
    """TODO: add docs"""

    pattern: Optional[str] = None
    """TODO: add docs"""

    preserve: bool = False
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        for to_name in self.to_names:  # type: ignore
            resource.schema.add_field(Field(name=to_name, type="string"))
        if not self.preserve:
            resource.schema.remove_field(self.name)
        processor = petl.split
        # NOTE: this condition needs to be improved
        if "(" in self.pattern:  # type: ignore
            processor = petl.capture
        resource.data = processor(  # type: ignore
            table,
            self.name,
            self.pattern,
            self.to_names,
            include_original=self.preserve,  # type: ignore
        )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "toNames", "pattern"],
        "properties": {
            "code": {},
            "name": {"type": "string"},
            "toNames": {},
            "pattern": {},
            "preserve": {},
        },
    }
