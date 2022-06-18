import petl
from typing import Optional
from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_search(Step):
    """Search rows"""

    code = "row-search"

    def __init__(
        self,
        *,
        regex: str,
        field_name: Optional[str] = None,
        negate: bool = False,
    ):
        self.regex = regex
        self.field_name = field_name
        self.negate = negate

    # Properties

    regex: str
    """TODO: add docs"""

    field_name: Optional[str]
    """TODO: add docs"""

    negate: bool
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        search = petl.searchcomplement if self.negate else petl.search
        if self.field_name:
            resource.data = search(table, self.field_name, self.regex)  # type: ignore
        else:
            resource.data = search(table, self.regex)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["regex"],
        "properties": {
            "code": {},
            "regex": {},
            "fieldName": {"type": "string"},
            "negate": {},
        },
    }
