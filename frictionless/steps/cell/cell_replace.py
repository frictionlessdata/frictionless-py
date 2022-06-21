import petl
from dataclasses import dataclass
from typing import Optional
from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


@dataclass
class cell_replace(Step):
    """Replace cell"""

    code = "cell-replace"

    # Properties

    pattern: str
    """TODO: add docs"""

    replace: str
    """TODO: add docs"""

    field_name: Optional[str] = None
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if not self.field_name:
            resource.data = table.replaceall(self.pattern, self.replace)  # type: ignore
        else:
            pattern = self.pattern
            function = petl.replace
            if pattern.startswith("<regex>"):  # type: ignore
                pattern = pattern.replace("<regex>", "")  # type: ignore
                function = petl.sub
            resource.data = function(table, self.field_name, pattern, self.replace)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["pattern"],
        "properties": {
            "code": {},
            "pattern": {"type": "string"},
            "replace": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
